# Tunmis Closet — Backend (Django + DRF)

REST API for the Tunmis Closet fashion e-commerce & portfolio site.

## Stack
Django 6, Django REST Framework, SimpleJWT auth, PostgreSQL (SQLite fallback for local dev), Cloudinary (media), Paystack (payments).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit values as needed
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Put that value in SECRET_KEY inside .env

python manage.py migrate
python manage.py createsuperuser   # for admin access
python manage.py runserver
```

API will be live at `http://127.0.0.1:8000/api/` and the health check at
`http://127.0.0.1:8000/health/`. Django admin is at `/admin/` by default; set
`ADMIN_URL` to use a less predictable path.

## Accounts, password reset and email verification

- New registrations receive a verification email. Existing users are marked
  verified by the migration.
- Set `REQUIRE_EMAIL_VERIFICATION=True` to block checkout until the email is
  verified. The frontend shows a resend option on the account page.
- Password reset and resend-verification endpoints are rate limited.
- Configure a real email backend before production. Locally the console
  backend prints verification and reset links in the server output.
- Changing a password invalidates existing refresh tokens.

## Going from SQLite to Postgres
Leave `DATABASE_URL` empty in `.env` to keep using SQLite. Production requires
PostgreSQL:
```
DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/tunmis_closet
```
then re-run `python manage.py migrate`.

## Media storage
Uploaded images use local disk in development. In production either set
`USE_CLOUDINARY=True` with the three `CLOUDINARY_*` values, or explicitly set
`ALLOW_LOCAL_MEDIA=True` if your web server persists and serves `/media/`.
Deployment fails fast if neither is configured.

## Paystack payments

1. Use test keys while testing. The backend requires both key prefixes to match
   `PAYSTACK_MODE` (`sk_test_`/`pk_test_` or `sk_live_`/`pk_live_`). Set
   `PAYSTACK_MODE=live` for customer-facing production. Test payments with
   `DEBUG=False` are blocked unless `ALLOW_TEST_PAYMENTS=True` is explicitly
   set for an isolated staging deployment.
2. Checkout flow: `POST /api/orders/checkout/` → `POST /api/payments/initialize/`
   → redirect to the returned `authorization_url` → Paystack redirects to
   `FRONTEND_URL/orders/<id>` → the authenticated order page calls
   `POST /api/payments/verify/` with the reference.
3. Set the Paystack webhook to `https://YOUR_API_HOST/api/payments/webhook/`.
   The endpoint verifies `X-Paystack-Signature` and confirms payments even if
   the buyer closes the browser.
4. Verification is ownership-checked and amount/currency-checked. A late
   success for a cancelled order stays cancelled but is flagged for refund.
5. Failed verification clears the stale checkout URL so the customer can retry
   with a new transaction.

## Order and refund workflow

Allowed transitions are enforced:

```
pending → paid/cancelled
paid → processing/shipped/cancelled
processing → shipped/delivered/cancelled
shipped → delivered
delivered/cancelled → (final)
```

Cancelling an order restocks it once. Cancelling a paid order sets
`refund_required`. Staff can issue a full Paystack refund from the Django admin
order action (“Refund captured payment via Paystack”) or
`POST /api/orders/<id>/refund/` as staff. Refund results are stored on the
payment and shown on the customer order page.

## Expiring unpaid orders

Checkout reserves stock immediately. Cancel abandoned orders hourly (or at
whatever interval suits you) so the stock returns to the shop:

```bash
python manage.py expire_pending_orders --minutes 60
```

Schedule this with your host's cron/scheduler. It is idempotent and returns
stock exactly once. It also verifies started Paystack transactions before
cancelling, so a paid-but-unconfirmed order is recovered.

## Tests and lint

```bash
pip install -r requirements-dev.txt   # ruff + coverage
ruff check .                          # lint
python manage.py test                 # tests
coverage run manage.py test && coverage report   # coverage (~81%)
```

Covers shipping quotes, checkout totals/stock reservation, cancellation,
email verification/password reset, order transitions, refunds, customer order
isolation, payment ownership/amount checks/webhook signatures, review
moderation, and contact submissions.

## Deployment

- The Render blueprint is at the repo root (`render.yaml`): web service, hourly
  `expire_pending_orders` cron job, and PostgreSQL. See `DEPLOYMENT.md`.
- Build/start commands are in `Procfile`; the included `Dockerfile` runs as a
  non-root user and exposes `/health/`. Its entrypoint collects static files
  but deliberately does not run schema migrations on every web-instance start.
- `docker compose up --build` runs a production-like PostgreSQL + API stack
  locally.
- Production settings validation fails fast when required values are unsafe or
  missing. Set at least:
  - `DEBUG=False`, a unique `SECRET_KEY` of 50+ characters, `ALLOWED_HOSTS`
  - `DATABASE_URL` (PostgreSQL), `FRONTEND_URL`, `CORS_ALLOWED_ORIGINS`,
    `CSRF_TRUSTED_ORIGINS`
  - `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY`
  - `USE_CLOUDINARY=True` plus Cloudinary credentials (or `ALLOW_LOCAL_MEDIA=True`)
  - SMTP variables (`EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_HOST_USER`,
    `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`) and `CONTACT_EMAIL`
- Run `python manage.py migrate --noinput` once as a release/pre-deploy task,
  then start the web process. Do not run migrations concurrently from every
  replica. `collectstatic` runs at container startup; non-container hosts
  should run `python manage.py collectstatic --noinput` during release.
- Schedule `expire_pending_orders` and back up PostgreSQL/media regularly.
- Rotate any Paystack key that has ever been shared or committed. Never commit
  `.env` or real credentials.

## API map

| Module | Base path |
|---|---|
| Auth (register/login/refresh/logout/password reset/email verify/profile/addresses) | `/api/auth/` |
| Categories | `/api/categories/` |
| Products (catalog + portfolio via `?portfolio=true`) | `/api/products/` |
| Cart | `/api/cart/` |
| Orders, shipping quotes, checkout, cancel, refund | `/api/orders/` |
| Payments (Paystack initialize/verify/webhook) | `/api/payments/` |
| Wishlist | `/api/wishlist/` |
| Reviews | `/api/reviews/` |
| Contact enquiries | `/api/contact/` |
| Health check | `/health/` |
| Sitemap (storefront URLs) | `/sitemap.xml` |

All endpoints return JSON. Authenticated requests use
`Authorization: Bearer <access_token>` from `/api/auth/login/`.
Successful login also returns a refresh token; use `/api/auth/login/refresh/`
to rotate it and `/api/auth/logout/` to blacklist it.
