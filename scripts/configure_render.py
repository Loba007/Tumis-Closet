#!/usr/bin/env python3
"""Configure existing manual Render services from render.yaml.

Reads secrets from backend/.env (or the process environment) and applies the
build/start commands, health check, schedule, and environment variables from
render.yaml to the services that already exist in your Render account.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    import yaml
except ImportError:  # pragma: no cover - depends on local dev dependencies
    sys.exit("PyYAML is required. Run: pip install -r backend/requirements-dev.txt")


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "render.yaml"
LOCAL_ENV = ROOT / "backend" / ".env"
API_BASE = "https://api.render.com/v1"

REDACT_VALUES: set[str] = set()


class RenderConfigError(Exception):
    """Raised when the Render API or local configuration cannot be used."""


def remember_secret(value: str) -> str:
    if len(value) >= 6:
        REDACT_VALUES.add(value)
    return value


def redact(text: str) -> str:
    for secret in sorted(REDACT_VALUES, key=len, reverse=True):
        text = text.replace(secret, "***")
    return text


def api(method: str, path: str, api_key: str, payload: object | None = None) -> object:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{API_BASE}{path}",
        data=body,
        method=method,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RenderConfigError(
            f"{method} {path} failed with {exc.code}: {redact(detail)[:600]}"
        ) from None
    except URLError as exc:
        raise RenderConfigError(f"{method} {path} failed: {exc.reason}") from None

    return json.loads(raw) if raw else None


def unwrap(items: object, key: str) -> list[dict]:
    if not isinstance(items, list):
        return []
    return [item.get(key, item) for item in items if isinstance(item, dict)]


def normalize(name: str) -> str:
    return "".join(char for char in name.lower() if char.isalnum())


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key.strip()] = value

    return values


def load_blueprint() -> tuple[dict, dict, dict, dict]:
    data = yaml.safe_load(BLUEPRINT.read_text(encoding="utf-8"))
    services = data.get("services", [])
    databases = data.get("databases", [])
    web = next((item for item in services if item.get("type") == "web"), None)
    cron = next((item for item in services if item.get("type") == "cron"), None)
    if not web or not cron or not databases:
        raise RenderConfigError("render.yaml must define a web service, a cron job, and a database")
    return data, web, cron, databases[0]


def pick_service(services: list[dict], spec: dict, env_prefix: str, fallback_type: str) -> dict:
    override = os.environ.get(f"RENDER_{env_prefix}_SERVICE_ID")
    if override:
        match = next((item for item in services if item.get("id") == override), None)
        if match is None:
            raise RenderConfigError(f"RENDER_{env_prefix}_SERVICE_ID={override} was not found")
        return match

    wanted = normalize(spec["name"])
    matches = [item for item in services if normalize(item.get("name", "")) == wanted]
    if not matches:
        matches = [
            item
            for item in services
            if wanted in normalize(item.get("name", ""))
            or normalize(item.get("name", "")) in wanted
        ]
    if not matches:
        matches = [item for item in services if item.get("type") == fallback_type]

    if len(matches) != 1:
        candidates = ", ".join(
            f"{item.get('name')} ({item.get('type')}, {item.get('id')})" for item in matches
        )
        raise RenderConfigError(
            f"Could not identify the {fallback_type} service. Candidates: {candidates or 'none'}. "
            f"Set RENDER_{env_prefix}_SERVICE_ID to the correct ID."
        )
    return matches[0]


def pick_database(databases: list[dict], spec: dict) -> dict:
    override = os.environ.get("RENDER_POSTGRES_ID")
    if override:
        match = next((item for item in databases if item.get("id") == override), None)
        if match is None:
            raise RenderConfigError(f"RENDER_POSTGRES_ID={override} was not found")
        return match

    wanted = normalize(spec["name"])
    matches = [item for item in databases if normalize(item.get("name", "")) == wanted]
    if not matches:
        matches = [
            item
            for item in databases
            if wanted in normalize(item.get("name", ""))
            or normalize(item.get("name", "")) in wanted
        ]
    if len(matches) != 1:
        candidates = ", ".join(
            f"{item.get('name')} ({item.get('id')})" for item in matches
        )
        raise RenderConfigError(
            f"Could not identify the Postgres database. Candidates: {candidates or 'none'}. "
            "Set RENDER_POSTGRES_ID to the correct ID."
        )
    return matches[0]


def desired_env(spec: dict, database_url: str, local_env: dict[str, str]) -> dict[str, str]:
    values: dict[str, str] = {}
    missing: list[str] = []

    for item in spec.get("envVars", []):
        key = item["key"]
        if "value" in item:
            values[key] = str(item["value"])
        elif "fromDatabase" in item:
            if item["fromDatabase"].get("property") != "connectionString":
                raise RenderConfigError(f"Unsupported fromDatabase property for {key}")
            values[key] = database_url
        elif item.get("sync") is False:
            value = os.environ[key] if key in os.environ else local_env.get(key, "")
            remember_secret(value)
            if not value and key != "SENTRY_DSN":
                missing.append(key)
            values[key] = value
        else:
            raise RenderConfigError(f"Unsupported envVar entry for {key}")

    if missing:
        raise RenderConfigError(
            "Missing secret values in backend/.env or the process environment: "
            + ", ".join(missing)
        )
    return values


def service_patch(spec: dict) -> dict:
    details: dict = {
        "runtime": spec.get("runtime", "python"),
        "envSpecificDetails": {"buildCommand": spec["buildCommand"]},
    }

    if spec.get("type") == "web":
        details["envSpecificDetails"]["startCommand"] = spec["startCommand"]
        details["preDeployCommand"] = spec["preDeployCommand"]
        details["healthCheckPath"] = spec["healthCheckPath"]
    else:
        details["envSpecificDetails"]["startCommand"] = spec["startCommand"]
        details["schedule"] = spec["schedule"]

    return {
        "rootDir": spec.get("rootDir", "backend"),
        "autoDeployTrigger": "commit",
        "serviceDetails": details,
    }


def merge_env_vars(api_key: str, service_id: str, desired: dict[str, str]) -> int:
    current = api("GET", f"/services/{service_id}/env-vars", api_key)
    merged: dict[str, str] = {}
    for item in current if isinstance(current, list) else []:
        entry = item.get("envVar", item) if isinstance(item, dict) else {}
        if "key" in entry and "value" in entry:
            merged[entry["key"]] = entry["value"]
    merged.update(desired)
    payload = [{"key": key, "value": value} for key, value in sorted(merged.items())]
    api("PUT", f"/services/{service_id}/env-vars", api_key, payload)
    return len(payload)


def configure_service(
    api_key: str,
    service: dict,
    spec: dict,
    database_url: str,
    local_env: dict[str, str],
    *,
    dry_run: bool,
) -> None:
    service_id = service["id"]
    patch = service_patch(spec)
    env_values = desired_env(spec, database_url, local_env)

    print(f"\n{spec['name']} -> {service.get('name')} ({service_id})")
    print(f"  rootDir: {patch['rootDir']}")
    print(f"  build: {patch['serviceDetails']['envSpecificDetails']['buildCommand']}")
    print(f"  start: {patch['serviceDetails']['envSpecificDetails']['startCommand']}")
    if "healthCheckPath" in patch["serviceDetails"]:
        print(f"  health: {patch['serviceDetails']['healthCheckPath']}")
        print(f"  pre-deploy: {patch['serviceDetails']['preDeployCommand']}")
    if "schedule" in patch["serviceDetails"]:
        print(f"  schedule: {patch['serviceDetails']['schedule']}")
    print(f"  env vars: {len(env_values)} from blueprint")

    if dry_run:
        return

    api("PATCH", f"/services/{service_id}", api_key, patch)
    total = merge_env_vars(api_key, service_id, env_values)
    print(f"  applied {total} total env vars (existing extras preserved)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print the plan without changing Render")
    parser.add_argument("--no-deploy", action="store_true", help="configure services but do not trigger deploys")
    parser.add_argument("--env-file", type=Path, default=LOCAL_ENV, help="local env file with secret values")
    args = parser.parse_args()

    try:
        _, web_spec, cron_spec, db_spec = load_blueprint()
        local_env = parse_env_file(args.env_file)

        api_key = os.environ.get("RENDER_API_KEY", "")
        remember_secret(api_key)
        if not api_key:
            raise RenderConfigError(
                "Set RENDER_API_KEY in your shell (Account Settings -> API Keys). "
                "Never commit it."
            )

        service_items = unwrap(api("GET", "/services?limit=100", api_key), "service")
        database_items = unwrap(api("GET", "/postgres?limit=100", api_key), "postgres")
        web_service = pick_service(service_items, web_spec, "WEB", "web_service")
        cron_service = pick_service(service_items, cron_spec, "CRON", "cron_job")
        database = pick_database(database_items, db_spec)

        connection = api("GET", f"/postgres/{database['id']}/connection-info", api_key)
        database_url = connection["internalConnectionString"]
        remember_secret(database_url)

        print(f"Database: {database.get('name')} ({database['id']})")
        configure_service(
            api_key, web_service, web_spec, database_url, local_env, dry_run=args.dry_run
        )
        configure_service(
            api_key, cron_service, cron_spec, database_url, local_env, dry_run=args.dry_run
        )

        if args.dry_run:
            print("\nDry run complete; no changes made.")
            return 0

        if not args.no_deploy:
            for service in (web_service, cron_service):
                api("POST", f"/services/{service['id']}/deploys", api_key, {"clearCache": "do_not_clear"})
                print(f"Triggered deploy for {service.get('name')}")

        print("\nRender configuration complete.")
        return 0
    except RenderConfigError as exc:
        print(f"error: {redact(str(exc))}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
