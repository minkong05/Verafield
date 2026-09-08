# apps/mill-dashboard

The web app a mill's procurement/sustainability staff use to see their own suppliers' compliance status and download evidence packs. Part of tech.md's "Output" layer (§6.1, Table 38), scoped here to the one deployable app that implements the mill-facing half of it.

## Roadmap features this implements

- [`07-supplier-mill-dashboard`](../../docs/roadmap/07-supplier-mill-dashboard.md) — live cleared / pending / frozen status per supplier, strictly isolated per mill (a mill only ever sees its own suppliers).

Evidence pack generation and renewal scheduling themselves are backend jobs (`backend/services/evidence_pack`, `backend/services/renewal`) — this app only displays their output and lets a mill trigger/download a pack, it doesn't generate one itself.

## Talks to

`backend/routes` — reads status and evidence-pack data. No direct database or service access.

## Frontend stack

The dashboard is scaffolded as a React + TypeScript single-page application using Vite.

```powershell
npm install
npm run dev
```

During local development, Vite proxies `/api` requests to the FastAPI service at
`http://localhost:8000`. Copy `.env.example` to `.env` to override the public API
base path for another environment. Run `npm run build` before committing frontend
changes.

## Data modes

Copy the example environment file before running locally:

```powershell
Copy-Item .env.example .env
```

| Variable | Development value | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `/api` | Uses the Vite proxy to reach FastAPI on port 8000. |
| `VITE_USE_MOCKS` | `true` | Keeps the UI usable without a database or backend process. Set to `false` for integration testing. |

Restart Vite after changing `.env`; Vite reads these values at startup.

## Implemented workflow

- Overview: supplier status counts, lapsed renewals and recent batches.
- Suppliers: search/filter and an on-demand compliance detail drawer.
- Review queue: derived from unresolved land, labour, deforestation, field, yield/licence, national-system and renewal records.
- Evidence packs: create a batch, inspect pack status, generate a pack and download the backend JSON snapshot.
- Renewals: current, lapsed and not-yet-issued annual review states.
- Light/dark themes and responsive navigation.
- Bearer-token login, session expiry, logout, mill account settings and password change.
- Admin mill selection, mill registry and user-account management.

The UI treats a `404` from an optional household compliance record as "not collected". Network errors and unexpected server failures remain visible as errors. Evidence-pack generation maps a `422` response to `Blocked`, because the backend refuses packs containing uncleared households.

## Real backend integration

From the repository root, start PostgreSQL and FastAPI using the backend instructions, then run the dashboard separately:

```powershell
cd apps\mill-dashboard
npm install
npm run dev
```

Set `VITE_USE_MOCKS=false`, then sign in with an account created by the backend admin workflow. A mill user receives its mill context from `/auth/me`; an admin selects a registered mill after login. Seed data must include households and plots to exercise batch creation; optional verification records may be absent and will appear as missing in the admin UI.

The dashboard sends the signed-in user's email as `created_by` and `generated_by` where the current backend schemas require a client-supplied identity string.

## Backend endpoints consumed

- `POST /auth/login`, `GET /auth/me`, `POST /auth/change-password`
- `GET/POST /mills`, `GET/PATCH /mills/{mill_id}`
- `GET/POST/PATCH /users`
- `GET /mills/{mill_id}/dashboard`
- `GET /mills/{mill_id}/renewal-status`
- `GET/POST /mills/{mill_id}/batches`
- `GET/POST /mills/{mill_id}/batches/{batch_id}/evidence-pack`
- Household gap, land, labour, consent, plot, deforestation, field-verification, yield/licence and national-system GET routes documented in [`docs/api-routes.md`](../../docs/api-routes.md).

## Known backend dependencies

- There is no household-detail GET route, so live mode cannot display household email/postal address from the dashboard response.
- There is no mill-wide plots route. Evidence-collection and plot-read routes are admin-only, so Create Batch is currently exposed only to admins, which can aggregate plots from supplier details. The backend permits a mill user to post a batch but does not provide that user an authorised way to discover eligible plot IDs.
- There is no review-queue route; the frontend derives the queue from verification responses.
- Evidence-collection routes are admin-only. Supplier evidence details and the derived review queue are therefore visible only to admins; mill users see the dashboard status supplied by the mill-facing endpoint.

## Non-goals

No cross-mill visibility, ever — multi-tenant isolation is enforced in `backend/db`, not just hidden in the UI.
