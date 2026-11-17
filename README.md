# Tunmis Closet

> "Fashion is the Language" — fashion e-commerce & portfolio site.

Full-stack scaffold built from the project PRD: Django REST Framework API
+ React/Vite/Tailwind storefront, gold-on-black brand theme, JWT auth,
PostgreSQL-ready (SQLite by default), Cloudinary media hooks, and Paystack
checkout — with automated backend tests covering the core purchase flow.

## Quick start

Two terminals:

```bash
# Terminal 1 — backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # then fill in values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` for the storefront and `http://localhost:8000/admin/`
for the Django admin (today's stand-in for the "admin dashboard" — add
categories, products, sizes/stock, and review orders there).

Full setup details, environment variables, and the API map are in
`backend/README.md` and `frontend/README.md`.

## What's wired up

| Area | Status |
|---|---|
| Auth (register/login/JWT refresh/logout, password reset, email verification, profile, addresses) | Working |
| Catalog & portfolio gallery (categories, products, sizes/stock) | Working |
| Cart | Working |
| Checkout, server-side shipping, stock reservation | Working |
| Order tracking, enforced transitions, cancellation, refunds, expiry/restock command | Working |
| Paystack initialize/verify/webhook, late-payment refund flags, staff refunds | Working, needs real API keys |
| Cloudinary media | Working via Django 6 `STORAGES`, local fallback until configured |
| Wishlist | Working |
| Reviews, moderation, verified-purchase badges | Working |
| Contact form + studio email notification | Working |
| Admin dashboard | Django admin for now (orders, reviews, refunds) |
| Backend tests | `python manage.py test` (60 tests, ~81% coverage) |
| Frontend tests | `npm test` (Vitest + Testing Library) |
| Lint | `ruff check .` (backend), `npm run lint` (frontend) |
| Health check | `GET /health/` |
| SEO | Dynamic `GET /sitemap.xml`; `robots.txt` in the storefront |
| Deployment | Render blueprint (`render.yaml`) + Vercel; see `DEPLOYMENT.md` |

## Brand

Gold (`#c8a24a`) on ink black, ivory shop surfaces, Cormorant Garamond for display
headings, Jost for everything else, with a thin gold-line flourish (a nod
to the crescent swoosh in the logo) used as a recurring divider. All of this
lives in `frontend/src/index.css`.

## Before going live

The full, step-by-step checklist lives in [`DEPLOYMENT.md`](DEPLOYMENT.md).
In short:

1. **Allow the production egress IP in Brevo.** Cloudinary, Paystack and Brevo
   SMTP are verified working locally (`send_mail` returned 1). For production,
   allow the server's egress IP in Brevo or disable the IP restriction; Render's
   default outbound IPs are not static.
2. Set `DEBUG=False`, a fresh 50+ char `SECRET_KEY`, PostgreSQL,
   `ALLOWED_HOSTS`, `FRONTEND_URL`, CORS/CSRF origins, Cloudinary, SMTP and the
   correct Paystack mode in the host dashboard. Startup fails fast on unsafe
   config.
3. Set the frontend's `VITE_API_URL` to the public HTTPS API URL ending in
   `/api`; production builds refuse local or non-HTTPS URLs.
4. Keep Paystack in test mode while exercising successful, failed, abandoned
   and late payments, webhook retries, stock release, cancellation and refunds.
   Then switch to the live pair, set `PAYSTACK_MODE=live` and
   `ALLOW_TEST_PAYMENTS=False` in `render.yaml`, and redeploy.
5. Run the hourly `expire_pending_orders` cron (included in `render.yaml`),
   enable database/media backups, and set `SENTRY_DSN` plus an uptime check.
6. Load real products/photography and confirm delivery rates, lead times,
   returns/privacy/terms and contact details with the studio. These are
   business claims, not code.
7. Deploy, run `./scripts/smoke_test.sh`, and test checkout and admin on real
   iOS and Android browsers.

## Development checks

```bash
make check   # backend lint + checks + tests, frontend lint + tests + build
```

See `DEPLOYMENT.md` for the production runbook and `render.yaml` for the
Render blueprint (web service + hourly cron + PostgreSQL).
