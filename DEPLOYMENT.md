# Deployment runbook

This is the production checklist for Tunmis Closet. The app is a Django API
(`backend/`) plus a React/Vite storefront (`frontend/`) that is expected to run
on two hosts (e.g. Render for the API, Vercel for the storefront).

> **Never commit secrets.** `.env`, `.env.production` and host dashboards are the
> only places real credentials belong.

## 0. Credential status

| Setting | Status |
|---|---|
| `CLOUDINARY_CLOUD_NAME` = `dw5fyvp1` | **Verified** — `api.ping()`, upload, URL and delete all succeed |
| `PAYSTACK_SECRET_KEY` / `PAYSTACK_PUBLIC_KEY` | **Verified** — `/balance` 200, `transaction/initialize` + `verify` succeed (test mode) |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` (Brevo) | **Verified** — login `ab595f001@smtp-brevo.com`, test `send_mail` returned 1. For production, allow the server's egress IP in Brevo (or disable the IP restriction); Render's default outbound IPs are not static |
| `DEFAULT_FROM_EMAIL` | Local uses the Brevo account email; production must use a domain-verified sender |

Rotate any credential that has been pasted into chat, email or source control.
Store the real values only in the host dashboard (Render) or an untracked
`.env.production`.

## 1. Backend on Render (Blueprint)

1. Push the repository to GitHub (the project is not a git repo yet: run
   `git init && git add . && git commit -m "Initial commit"`).
2. In Render: **New → Blueprint**, select the repo. `render.yaml` creates:
   - `tunmis-closet-api` web service (Gunicorn, health check `/health/`)
   - `tunmis-closet-expire-orders` hourly cron job
   - `tunmis-closet-db` PostgreSQL database
3. Fill the `sync: false` environment variables in the dashboard for **both**
   the web service and the cron job:

| Variable | Value |
|---|---|
| `SECRET_KEY` | `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `CLOUDINARY_CLOUD_NAME` / `_API_KEY` / `_API_SECRET` | Cloudinary dashboard |
| `PAYSTACK_SECRET_KEY` / `PAYSTACK_PUBLIC_KEY` | Start with `sk_test_` / `pk_test_` |
| `EMAIL_HOST_PASSWORD` | Brevo SMTP key |
| `SENTRY_DSN` | Optional; enables error tracking |

`DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`, `FRONTEND_URL`, CORS/CSRF origins,
`DEFAULT_FROM_EMAIL`, `CONTACT_EMAIL`, security flags, `PAYSTACK_MODE`,
`USE_CLOUDINARY`, `EMAIL_BACKEND` and `REQUIRE_EMAIL_VERIFICATION` are already
set by the blueprint. The app refuses to boot if any required production value
is unsafe.

`render.yaml` starts in **test mode** (`PAYSTACK_MODE=test`,
`ALLOW_TEST_PAYMENTS=True`) so a public staging deploy boots with the test keys
you already verified. This is not customer-facing: before accepting orders, set
`PAYSTACK_MODE=live` and `ALLOW_TEST_PAYMENTS=False` and replace the Paystack
keys with the live pair.

4. Add a custom domain (`api.tunmiscloset.com`) and let Render issue TLS.
5. First deploy runs `collectstatic` (build) and `migrate` (pre-deploy).
6. Seed or load real catalog data:
   ```bash
   # Demo data (optional)
   python manage.py seed_products
   # or add products/categories/sizes in /studio-admin/
   ```
   Run this from the Render shell, never by committing `db.sqlite3`.

### Manual (non-blueprint) deploy

Set the same env vars, then:

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 60
```

#### Sync an already-created manual service

If the web/cron services were created manually, Render does **not** apply
`render.yaml`. `scripts/configure_render.py` reads the blueprint, pulls secrets
from `backend/.env`, resolves `DATABASE_URL` from Render Postgres connection
info, and patches both services through the Render API.

1. Create an API key in Render → Account Settings → API Keys with read/write
   access to services, Postgres and deploys.
2. Install dev dependencies: `pip install -r backend/requirements-dev.txt`.
3. Preview without changing anything:
   ```bash
   RENDER_API_KEY=... make render-config-dry-run
   ```
4. Apply and trigger deploys:
   ```bash
   RENDER_API_KEY=... make render-config
   ```

If auto-discovery picks the wrong resources, set `RENDER_WEB_SERVICE_ID`,
`RENDER_CRON_SERVICE_ID` and/or `RENDER_POSTGRES_ID`. Never commit the API key.
Use `python3 scripts/configure_render.py --no-deploy` to configure without
triggering a deploy.

## 2. Frontend on Vercel

1. Import the repo, set **Root Directory** to `frontend`.
2. Build command `npm run build`, output `dist`.
3. Environment variable: `VITE_API_URL=https://api.tunmiscloset.com/api`.
   Production builds fail if this is missing, non-HTTPS or not ending in `/api`.
4. Add the custom domain `www.tunmiscloset.com` and redeploy.
5. `vercel.json` already applies CSP/HSTS/frame/MIME/referrer headers and
   rewrites SPA routes.

## 3. Paystack

1. Keep test keys and `PAYSTACK_MODE=test` while validating.
2. Webhook URL: `https://api.tunmiscloset.com/api/payments/webhook/`
   (Dashboard → Settings → API Keys & Webhooks).
3. Exercise: successful, failed, abandoned and late payments; webhook retries;
   stock release; customer cancellation; staff refund.
4. Only then swap to the live pair, set `PAYSTACK_MODE=live` and
   `ALLOW_TEST_PAYMENTS=False` (in `render.yaml` or the dashboard), redeploy, and
   run one small real payment + refund.

## 4. Background work

No worker/Redis is required. The `render.yaml` cron runs:

```bash
python manage.py expire_pending_orders --minutes 60
```

It is idempotent, restocks expired unpaid orders, and verifies started Paystack
transactions before cancelling. If you leave Render, schedule the same command
hourly with the host's cron/Cron Job. Emails are sent synchronously after the
request commits; at higher volume move them to a queue (Celery/RQ).

## 5. Backups and monitoring

- Enable Render Postgres backups / point-in-time recovery, and take a manual
  backup before each release.
- Cloudinary stores media; enable account backups and keep the API key scoped.
- Set `SENTRY_DSN` (sentry-sdk is already installed) and an uptime check on
  `https://api.tunmiscloset.com/health/`.
- Ship server logs to the host's log stream; alert on 5xx, failed emails,
  webhook failures and cron errors.

### Scale notes

- DRF throttling currently uses Django's default local-memory cache, so limits
  are per worker, not global. If abuse becomes a problem, set a shared cache
  (Redis) via `CACHES`; no other code changes are needed.
- Email sends happen synchronously after commit. At volume, move
  `orders/notifications.py`, `contact/views.py` and `accounts/emails.py` to a
  Celery/RQ task queue.
- Gunicorn runs 3 workers by default; raise `--workers` on larger instances and
  keep `--timeout 60`.

## 6. Post-deploy smoke test

```bash
API=https://api.tunmiscloset.com ./scripts/smoke_test.sh
```

Then on real iOS and Android browsers: browse, search, add to bag, checkout,
pay (test mode), verify, cancel, and open an order. Check the admin at
`/studio-admin/`.

## 7. Going-live checklist

- [ ] `DEBUG=False`, unique 50+ char `SECRET_KEY`, real `ALLOWED_HOSTS`
- [ ] PostgreSQL connected, migrations applied, demo data removed
- [ ] Cloudinary uploads working (upload a product image)
- [ ] Brevo SMTP sends order confirmation, verification and reset emails
- [ ] Brevo sender/domain authenticated (SPF/DKIM) and production egress IP allowed (or IP restriction disabled)
- [ ] Paystack webhook verified; live keys + `PAYSTACK_MODE=live`
- [ ] `REQUIRE_EMAIL_VERIFICATION=True`
- [ ] HTTPS, HSTS, secure cookies, CORS/CSRF limited to the storefront origin
- [ ] Cron running and logs clean
- [ ] Backups enabled and a restore tested
- [ ] Sentry + uptime alerting active
- [ ] Shipping prices, lead times, returns and contact details confirmed with the studio
- [ ] Privacy/terms/returns copy reviewed
- [ ] `robots.txt` deployed and `/sitemap.xml` submitted in Search Console
- [ ] Secrets rotated and `.env*` files not tracked
