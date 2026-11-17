# Tunmis Closet — Frontend (React + Vite + Tailwind)

The storefront and portfolio site for Tunmis Closet. Gold-on-black brand
theme, built against the Django REST API in `../backend`.

## Setup

```bash
npm install
cp .env.example .env     # defaults already point at the local backend
npm run dev
```

App runs at `http://localhost:5173`. Make sure the backend is running at
`http://localhost:8000` first (see `../backend/README.md`).

## Structure

```
src/
  api/         axios calls, one file per backend module (auth, products, cart,
               orders, payments, wishlist, reviews, contact)
  context/     AuthContext (JWT session) and CartContext (cart state)
  components/  Navbar, Footer, ProductCard, GoldFlourish, ProtectedRoute,
               ErrorBoundary, ScrollToTop
  hooks/       usePageMeta (titles, descriptions, Open Graph, robots)
  pages/       Home, Shop, ProductDetail, Portfolio, About, FAQ, Contact,
               Cart, Checkout, Login, Register, ForgotPassword, ResetPassword,
               VerifyEmail, Wishlist, Orders, OrderDetail, Account, SizeGuide,
               PolicyPage, NotFound
```

## Brand theme

Color tokens and fonts live in `src/index.css` under the Tailwind v4 `@theme`
block: `--color-ink` (near-black), `--color-gold` / `--color-gold-light` /
`--color-gold-dark`, `--color-ivory` / `--color-ivory-deep` for shop surfaces,
and `--color-stone` for muted text. Display headings use Cormorant Garamond; body/UI
text and tracked-out labels use Jost (`.label-track` utility class).

## Payment flow
Checkout asks the API for a server-side shipping quote, creates an order, then
calls `/api/payments/initialize/` and redirects to the returned Paystack
`authorization_url`. Paystack returns to `/orders/<id>?reference=...`, where
the authenticated order page verifies the transaction and shows the
paid/cancelled/refund state. Failed verification clears the old checkout URL,
so “Pay Now” starts a fresh attempt. Until real Paystack keys are set in the
backend `.env`, payment will fail with a clear message — the order itself is
still saved and can be retried from its order page.

## Account recovery and email verification
`/forgot-password` requests a reset link; `/reset-password?uid=...&token=...`
sets the new password. New registrations receive a verification link to
`/verify-email`; unverified customers see a resend option on `/account`.
When the backend enables `REQUIRE_EMAIL_VERIFICATION`, checkout is blocked
until the email is confirmed.

## Security notes
- Access tokens are short-lived; concurrent 401 responses share one refresh
  request, and a failed refresh clears the local session.
- `vercel.json` adds CSP, HSTS, frame protection, MIME sniffing protection,
  a strict referrer policy and a restrictive permissions policy.
- Do not put secrets in `VITE_*` variables; they are bundled into the browser
  build. Only `VITE_API_URL` belongs there.

## Tests and lint

```bash
npm run lint            # ESLint
npm test                # Vitest + Testing Library
npm run test:coverage   # coverage report
npm run audit           # production dependency audit
```

## Deploying
`npm run build` outputs `dist/`. For Vercel, `vercel.json` rewrites
client-side routes to `index.html` and adds security headers. Set
`VITE_API_URL` to the public backend URL, e.g. `https://api.example.com/api`.
Run `npm audit --omit=dev --registry=https://registry.npmjs.org` before
release; production dependencies should report zero vulnerabilities.
