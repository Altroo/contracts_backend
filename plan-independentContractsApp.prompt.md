# Plan: Independent Contracts App (Backend + Frontend + Nginx)

> **Domain overview**
> | App | Frontend | Backend API |
> |---|---|---|
> | Facturation | `facturation.elbouazzatiholding.ma` | `facturation_api.elbouazzatiholding.ma` |
> | Contracts | `contracts.elbouazzatiholding.ma` | `contracts_api.elbouazzatiholding.ma` |
> | Portal (future) | `www.elbouazzatiholding.ma` | — |
>
> `www.elbouazzatiholding.ma` / `elbouazzatiholding.ma` is **reserved** for a future apps portal — no app should ever claim this root domain.

**TL;DR**: Scaffold two greenfield apps — `contracts_backend` (Django) and `contracts_frontend` (Next.js) — by copying and trimming the facturation stack. The contracts backend gets: `account`, `contract`, `core`, `ws` (no company, no client/article/devi/etc.), Celery on Redis DB 1, port 8001. Since contracts is for one company only, the `company` app and `Membership`-based role system are dropped; permissions simplify to `IsAuthenticated` / `is_staff`. The contracts frontend gets: auth pages, contracts pages, settings (profil + password), and a trimmed drawer (Contrats | Paramètres). Then remove the `contract` app from facturation, and add 2 server blocks to the shared nginx. Ports: **backend 8001**, **frontend 3001** (both exposed to host; nginx uses `host.docker.internal:8001` and `host.docker.internal:3001`).

---

## PHASE 0 — Infrastructure prerequisites *(do before any code deployment)*

**Step 0a — DNS records**
Create A records (or CNAMEs pointing to the same server IP) for all four new subdomains:
- `facturation.elbouazzatiholding.ma`
- `facturation_api.elbouazzatiholding.ma`
- `contracts.elbouazzatiholding.ma`
- `contracts_api.elbouazzatiholding.ma`

Also ensure `www.elbouazzatiholding.ma` and bare `elbouazzatiholding.ma` point to the server (they already likely do).

**Step 0b — SSL certificate**
The current cert covers only specific hostnames. Expand or reissue it to cover all subdomains:
- Request a wildcard cert `*.elbouazzatiholding.ma` via Certbot: `certbot certonly --nginx -d elbouazzatiholding.ma -d *.elbouazzatiholding.ma`
- Replace `/etc/ssl/certs/fullchain.pem` and `privkey.pem` on the server with the new cert
- `nginx -t && nginx -s reload` to apply
- Verify: `curl -vI https://contracts_api.elbouazzatiholding.ma/` — must show valid TLS before any service is deployed there

---

## PHASE 1 — contracts_backend

**Step 1 — Project bootstrap**
- `manage.py` + `contracts_backend/` package folder (settings, urls, asgi, wsgi)
- `requirements.txt` — identical to facturation_backend's

**Step 2 — Copy apps verbatim from facturation_backend**
- `account/` — copy entire app; then make these adjustments:
  - **Remove `Membership` model** and `MembershipSerializer` — depend on `company.Company`
  - In `account/tasks.py`: **remove `send_csv_example_email` task** and its helper — it references article import templates that don't exist in contracts
  - In `account/serializers.py`: **remove `companies` field** from `CreateAccountSerializer` (no memberships); remove `MembershipSerializer` import
  - In `account/views.py`: **remove `ROLES_RESTRICTED` checks** — replace all role-based permission guards with plain `permissions.IsAdminUser`
  - In `account/filters.py`: remove any company/membership filter fields
- `core/` — copy entire app; then:
  - `core/views.py`: **delete the entire `BaseDocumentListCreateView` class and all other document-base view classes** — they import `from client.models import Client` which does not exist in contracts and will cause an `ImportError` on startup. Remove also the top-level `from client.models import Client` and `from account.models import Membership` imports. **Remove `CompanyAccessMixin`** entirely. The resulting `core/views.py` can be nearly empty (just the logger and any remaining standalone helpers).
  - `core/permissions.py`: **rewrite all `can_*` functions** — drop the `company_id` parameter everywhere; new model:
    - `can_view(user)` → `return True` (any authenticated user can read)
    - `can_print(user)` → `return True` (any authenticated user can print/download)
    - `can_create(user)` → `return user.is_staff`
    - `can_update(user)` → `return user.is_staff`
    - `can_delete(user)` → `return user.is_staff`
    - Remove `get_user_role`, `is_caissier`, `is_comptable`, `is_commercial`, `is_lecture`, and the role-constant imports — they all depend on `Membership` which does not exist in contracts.
- `ws/` — copy entire app (needed for real-time avatar push after upload)

**Step 3 — Copy + adjust `contract/`**
- Copy entire app from facturation_backend
- In `contract/models.py`:
  - **Remove** `company = ForeignKey("company.Company", ...)` — single-company app, no company scoping needed
  - **Remove** `client = ForeignKey("client.Client", ...)` — already fully denormalized (`client_nom`, `client_adresse`, `client_tel`, `client_email` are embedded)
  - **Remove** `unique_together = [("numero_contrat", "company")]` — replace with `unique=True` on `numero_contrat` field directly
  - **Remove** compound indexes that reference `company` field
- In `contract/serializers.py`:
  - Remove `"company"` and `"client"` from all `Meta.fields` lists
  - Update `get_client_name` to return only `obj.client_nom` (no FK lookup)
- In `contract/views.py`:
  - Remove all `CompanyAccessMixin` usage and company_id / membership checks
  - All views keep `permission_classes = (permissions.IsAuthenticated,)` as the class-level guard (ensures login)
  - Inside each view method, enforce the new model:
    - GET (list/detail), PDF, DOC: no extra check — all authenticated users allowed
    - POST (create): raise `PermissionDenied` unless `can_create(request.user)` (i.e. `is_staff`)
    - PUT (update) + PATCH (status): raise `PermissionDenied` unless `can_update(request.user)`
    - DELETE (single + bulk): raise `PermissionDenied` unless `can_delete(request.user)`
  - Remove `.select_related("client", "company", ...)` — keep only `created_by_user`
- In `contract/filters.py`: remove any `company` filter field
- In `contract/utils.py` (`get_next_numero_contrat`): remove `company_id` parameter, query globally
- Copy `contract/pdf.py` and `contract/doc.py`; then patch both:
  - `pdf.py` has 3 references to `contract.company.raison_sociale` (lines ~252, ~421, ~451 — exact lines may shift). Replace every `c.company.raison_sociale or "CASA DI LUSSO"` with the hardcoded string `"CASA DI LUSSO"` (single-company app, no FK lookup needed).
  - `doc.py` has 2 references to `c.company.raison_sociale` (lines ~257, ~381). Apply the same replacement.
  - In `contract/views.py`, `ContractPDFView._get_contract()` and `ContractDOCView._get_contract()` both call `.select_related("company", "client", "created_by_user")`. Remove `"company"` and `"client"` from both — becomes `.select_related("created_by_user")` only.
  - Update permission checks in `ContractPDFView.get()` and `ContractDOCView.get()`: remove `_has_membership` check; `can_print(user)` now always returns `True` so no explicit check needed — the class-level `IsAuthenticated` guard is sufficient.
- Copy `contract/admin.py`; then patch: remove `"company"` from `list_display` and from `list_filter`. Also update any `select_related` in admin that includes `"company"`.

**Step 4 — `contracts_backend/settings.py`**
- Copy facturation settings, then adjust:
  - `INSTALLED_APPS`: keep `account`, `contract`, `core`, `ws` — remove `company`, `parameter`, `client`, `article`, `devi`, `facture_proforma`, `facture_client`, `bon_de_livraison`, `reglement`, `dashboard`
  - `AUTH_USER_MODEL = "account.CustomUser"` (note: same model, but now under "account" app label — verify the app label in `account/apps.py` is `"account"`)
  - `JWT_AUTH_COOKIE = "contracts-jwt-access"`, `JWT_AUTH_REFRESH_COOKIE = "contracts-jwt-refresh"` — avoids cookie collision with facturation
  - Keep all security, CORS, axes, channels settings identical
  - Celery: `CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"` and `CELERY_RESULT_BACKEND` → same `/1` (Redis DB 1)
  - `ROOT_URLCONF = "contracts_backend.urls"`
  - `ASGI_APPLICATION = "contracts_backend.asgi.application"`
  - `SITE_ID = 1` remains — Django creates the default `example.com` row automatically on `migrate`; no manual population needed (facturation works the same way)

**Step 5 — `contracts_backend/urls.py`**
```
/api/health/                → health_check
/api/account/               → account.urls
/api/contract/              → contract.urls
/gestion-interne-x7k2/     → admin.site.urls
```

**Step 6 — `contracts_backend/celery_conf.py`**
- Copy from facturation, change app name to `"contracts_backend"`, broker/result on Redis DB 1
- `autodiscover_tasks(packages=["account.tasks"])` — same tasks

**Step 7 — Email templates**
- In `account/templates/password_reset.html`: change every "Facturation" occurrence → "Contrats", change title to "Renouvelez votre mot de passe - Contrats"
- In `account/templates/new_account.html`: change every "facturation" → "contrats", title → "Invitation à l'application de contrats"
- In `account/templates/new_password.html`: same rename

**Step 8 — Fresh migrations**
- Delete any copied migrations (they reference the old DB)
- `python manage.py makemigrations` for all 4 apps (`account`, `contract`, `core`, `ws`) → fresh initial migrations

**Step 9 — `docker-compose.yml`**
- Copy facturation's docker-compose, adjust:
  - `web` service: expose port `"8001:8000"` (host:container)
  - **Remove the `redis` service entirely** — contracts shares the existing Redis instance already running on the host for facturation
  - `celery` service: remove `depends_on: redis`; set `CELERY_BROKER_URL=redis://host.docker.internal:6379/1` and `CELERY_RESULT_BACKEND=redis://host.docker.internal:6379/1`
  - `celery` command: `celery -A contracts_backend.celery_conf worker --loglevel=info --concurrency=32 -E -P gevent`
  - In `settings.py` Channel Layers config: use `host.docker.internal` and port `6379` (same host Redis)
  - Keep local `db` service — database name in `.env`: `POSTGRES_DB=casadilusso-contrats`

**Step 10 — `Dockerfile`**
- Identical to facturation_backend's Dockerfile (same Python/Daphne stack)

**Step 11 — `.env.example`**
```
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=contracts_api.elbouazzatiholding.ma
CORS_ALLOWED_ORIGINS=https://contracts.elbouazzatiholding.ma
CSRF_TRUSTED_ORIGINS=https://contracts_api.elbouazzatiholding.ma
POSTGRES_DB=casadilusso-contrats
POSTGRES_USER=dgsjgsmqdcldlm
POSTGRES_PASSWORD=
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_HOST=host.docker.internal
REDIS_PORT=6379
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
API_URL=https://contracts_api.elbouazzatiholding.ma
SECURE_SSL_REDIRECT=True
```

---

## PHASE 2 — contracts_frontend

**Step 12 — Bootstrap Next.js app**
- **Do not run `create-next-app`** — manually create the directory structure and copy root config files to avoid overwriting with boilerplate
- Copy root config files: `package.json` (same dependency versions), `next.config.ts`, `tsconfig.json`, `eslint.config.mjs`, `jest.config.ts`, `jest.setup.ts`, `qodana.yaml`, `env.d.ts`, `next-env.d.ts`
- In `next.config.ts`: adjust `remotePatterns` hostname to `contracts_api.elbouazzatiholding.ma`
- Copy `public/` directory — swap logo/favicon with contracts branding if needed
- Copy `proxy.ts` from facturation_frontend root if it exists (Next.js API middleware)

**Step 13 — Environment variables**
- `env.d.ts` is already copied in Step 12 — its type declarations stay the same
- Create `.env.local` (dev) and `.env.production` with:
  - `NEXTAUTH_URL=https://contracts.elbouazzatiholding.ma` (production) / `http://localhost:3001` (dev) — **required by NextAuth in production**
  - `NEXTAUTH_SECRET=<new random secret — do not reuse facturation's>`
  - `NEXT_PUBLIC_ACCOUNT_LOGIN=https://contracts_api.elbouazzatiholding.ma/api/account/login/`
  - `NEXT_PUBLIC_ACCOUNT_REFRESH_TOKEN=https://contracts_api.elbouazzatiholding.ma/api/account/token_refresh/`
  - `NEXT_PUBLIC_API_ROOT_URL=https://contracts_api.elbouazzatiholding.ma`

**Step 14 — `src/auth.ts`**
- Copy from facturation_frontend unchanged — all env vars drive the API endpoints, no hardcoded facturation references

**Step 15 — `src/store/`**
- Copy `slices/_initSlice` and `slices/accountSlice` only — **skip `companiesSlice`** (no company switching needed)
- Copy `services/account.ts` and `services/contract.ts` only — **skip `services/company.ts`**
- Rewrite `store.ts` — combine only those 2 RTK Query services + 2 slices
- Copy `store/selectors/index.ts`; then remove the `getUserCompaniesState` selector and its `CompaniesUserCompaniesType` import — keep only `_init` and `account` selectors. Also update `RootState` type in `store.ts` accordingly (no `companies` key).
- Copy sagas: `accountSaga.ts`, `wsSaga.ts`, `_initSaga.ts` — **skip `companiesSaga.ts`**. Rewrite `sagas/index.ts` to only spawn `accountSaga`, `wsSaga`, and `_initSaga` — remove the `companiesSaga` import and `fork`/`spawn` call.

**Step 16 — `src/contexts/`**
- Copy all 4 context files (`InitContext.tsx`, `initEffects.tsx`, `toastContext.tsx`, `portal.tsx`)
- In `initEffects.tsx`: **remove** the companies query (`useGetUserCompaniesQuery`) and `setUserCompanies` dispatch — no company selector needed; keep only profil + groups queries

**Step 17 — `src/providers/`**
- Copy unchanged

**Step 18 — `src/components/formikElements/`**
- Copy entire directory unchanged

**Step 19 — `src/components/htmlElements/`**
- Copy entire directory unchanged

**Step 20 — `src/styles/`**
- Copy entire SASS modules directory unchanged

**Step 21 — `src/utils/`**
- Copy entire utils directory (API clients, route constants, theme, etc.)
- In route constants: keep `LOGIN`, `DASHBOARD`, `CONTRACT_*`, `SETTINGS_*` — remove `DEVIS_*`, `FACTURE_*`, etc.

**Step 22 — `src/types/` and `src/models/`**
- Copy from facturation_frontend — remove document-specific types (devis, facture, etc.) and company types; keep account and contract types only

**Step 23 — Navigation bar**
- Copy `src/components/layouts/navigationBar/navigationBar.tsx`
- Rewrite `getNavigationMenu()` to return only:
  - **Contrats** (contracts list)
  - **Paramètres** → sub-items: Mon Profil, Changer le mot de passe
- Remove all document menu items (Devis, Facture, BDL, Articles, Clients, Sociétés, Utilisateurs, Règlements)
- **Remove `hasCasaDiLusso` flag and all company-membership-based menu conditions** — contracts always shows its full menu to all authenticated users
- Remove `userCompaniesState` selector and `companiesSlice` usage from the navigation bar
- Keep top-bar logout + "Accès Admin" (isStaff) buttons unchanged

**Step 24 — Auth layout + protected wrapper**
- Copy `src/components/layouts/auth/` unchanged
- Copy `src/components/layouts/protected/` unchanged

**Step 25 — Auth pages**
- Copy `src/components/pages/auth/login/login.tsx` unchanged
- Copy `src/components/pages/auth/reset-password/` unchanged

**Step 26 — Dashboard pages**
- Copy `src/components/pages/dashboard/contracts/` all 3 files (list, form, view), then adjust:
  - `contract-form.tsx`: **remove `useGetClientListQuery`** import and the client dropdown UI — the form already has manual text fields (`client_nom`, `client_adresse`, etc.); also remove `company_id` param from the contract submit payload and `useGetUserCompaniesQuery`
  - `contract-list.tsx`: **remove `company_id` query param and company selector** — list fetches all contracts unconditionally for the single-company app
  - `contract-view.tsx`: no changes needed
- Copy `src/components/pages/dashboard/settings/` (profil + change password pages)
- Copy `src/components/pages/dashboard/shared/` — **skip `companyDocumentsWrapperView`**; copy only `pdfLanguageModal` and shared action modal components used by the contracts pages

**Step 27 — App router (`src/app/`)**
- `(auth)/login/page.tsx` — copy
- `(auth)/reset-password/page.tsx` — copy
- `dashboard/layout.tsx` — copy (NavigationBar wrapper)
- `dashboard/page.tsx` — redirect to `/dashboard/contracts`
- `dashboard/contracts/page.tsx` — copy
- `dashboard/contracts/new/page.tsx` — copy
- `dashboard/contracts/[id]/page.tsx` — copy
- `dashboard/settings/profil/page.tsx` — copy
- `dashboard/settings/password/page.tsx` — copy
- `api/auth/[...nextauth]/route.ts` — copy
- `layout.tsx` (root) — copy
- `page.tsx` — redirect to `/login`
- `not-found.tsx` — copy

**Step 28 — `docker-compose.yml`** (contracts_frontend)
- Copy facturation_frontend docker-compose
- `web` service port: `"3001:3000"`
- No nginx service here — nginx is shared on the server

**Step 29 — `Dockerfile`**
- Copy facturation_frontend's Dockerfile unchanged

**Step 30 — ESLint unused-code cleanup**
- After all files are copied and store/contexts are trimmed, run `npx next lint` to surface unused imports and variables
- Then run `npx eslint src/ --rule '{"no-unused-vars": ["error", {"vars": "all"}]}' --ext .ts,.tsx` to catch any remaining unused exports/components
- Delete any component files (formikElements, htmlElements, shared, etc.) that are entirely unused after the above passes — no document-form components, no company selector components
- Re-run `npm run build` to confirm 0 TypeScript / lint errors before proceeding

---

## PHASE 3 — Facturation domain rename

> **Deployment sequence**: Phases 1 & 2 (build contracts apps) can be done in parallel with Phase 0. Deploy contracts on its new domains and test fully. **Only then** notify facturation users, then execute Phase 3 (rename facturation domains) and Phase 5 (nginx) in one coordinated maintenance window to minimise downtime.

**Step 31 — Update facturation_backend environment & settings**
- In `facturation_backend/.env` (production): update `ALLOWED_HOSTS` to include `facturation_api.elbouazzatiholding.ma` (remove bare `api.elbouazzatiholding.ma`)
- Update `CORS_ALLOWED_ORIGINS` to `https://facturation.elbouazzatiholding.ma`
- Update `CSRF_TRUSTED_ORIGINS` to `https://facturation_api.elbouazzatiholding.ma`

**Step 32 — Update facturation_frontend environment**
- In `.env.local` / `.env.production`: update all `NEXT_PUBLIC_*` API URLs to point to `facturation_api.elbouazzatiholding.ma`
- Update `next.config.ts` `remotePatterns` hostname to `facturation_api.elbouazzatiholding.ma`

**Step 33 — Nginx: rename facturation server blocks**
- `server_name api.elbouazzatiholding.ma` → `facturation_api.elbouazzatiholding.ma`
- `server_name elbouazzatiholding.ma` → `facturation.elbouazzatiholding.ma`
- Keep `www.elbouazzatiholding.ma` and bare `elbouazzatiholding.ma` **unassigned** (or add a placeholder block returning 200 with a simple coming-soon page — do not proxy to any app)

---

## PHASE 4 — Facturation code cleanup

**Step 34 — `facturation_backend`**
- Remove `"contract.apps.ContractConfig"` from `INSTALLED_APPS` in `facturation_backend/settings.py`
- Remove `path("api/contract/", include("contract.urls"))` from `facturation_backend/urls.py`
- Delete `facturation_backend/contract/` directory entirely
- Run `python manage.py migrate contract zero` then remove migrations

**Step 35 — `facturation_frontend`**
- Remove `dashboard/contracts/` from `src/app/`
- Remove `src/components/pages/dashboard/contracts/`
- Remove `contractApi` from `src/store/services/contract.ts` and from `store.ts` combineReducers
- Remove "Contrats" from navigation menu in `src/components/layouts/navigationBar/navigationBar.tsx`

---

## PHASE 5 — Nginx: add contracts blocks

**Step 36 — Add 2 server blocks to `/etc/facturation_frontend/nginx/conf.d/app.conf`**

Add **before** the catch-all block (facturation blocks are already renamed in Phase 3):

**Block A — `contracts_api.elbouazzatiholding.ma`**
- Identical to the `facturation_api.elbouazzatiholding.ma` block
- `server_name contracts_api.elbouazzatiholding.ma`
- All `proxy_pass` directives: `host.docker.internal:8001` (port 8001)
- No `/ws` location block needed (contracts has no real-time WebSocket)

**Block B — `contracts.elbouazzatiholding.ma`**
- Identical to the `facturation.elbouazzatiholding.ma` block
- `server_name contracts.elbouazzatiholding.ma`
- All `proxy_pass` directives: `host.docker.internal:3001` (port 3001)

**Block C — `www.elbouazzatiholding.ma` / `elbouazzatiholding.ma` (portal placeholder)**
- `server_name elbouazzatiholding.ma www.elbouazzatiholding.ma`
- For now: return a minimal 200 or redirect to `facturation.elbouazzatiholding.ma` until the portal is built
- Must sit **between** the app blocks and the catch-all so the catch-all never swallows the root domain

> The catch-all `return 444` block stays last and unchanged.

---

## Verification

1. **contracts_backend**: `python manage.py check` → 0 errors; `python manage.py migrate` → all tables created in `casadilusso-contrats` DB
2. **contracts_frontend**: `npm run build` → 0 TypeScript errors; login flow works against `contracts_api.*`
3. **facturation_backend**: `python manage.py check` + `python manage.py showmigrations` → contract app gone, no broken references
4. **Nginx**: `nginx -t` → configuration test passes
   - `curl -I https://facturation_api.elbouazzatiholding.ma/api/health/` → 200
   - `curl -I https://contracts_api.elbouazzatiholding.ma/api/health/` → 200
   - `curl -I https://www.elbouazzatiholding.ma/` → 200 (portal placeholder)
   - `curl -I https://1.2.3.4/` → connection dropped (catch-all 444)

---

## Key Decisions

- **Redis DB 1** for contracts Celery — avoids task queue collision with facturation (DB 0)
- **No `company` module** — contracts_backend is single-company; `company` FK removed from `Contract`, `Membership` model dropped from `account`, `CompanyAccessMixin` replaced with plain `IsAuthenticated`/`is_staff` checks
- **Remove `client` FK from Contract** — already fully denormalized; makes the app standalone with no `client` app dependency
- **JWT cookies renamed** (`contracts-jwt-access`) — prevents session collision when both apps run on the same browser
- **Ports 8001 / 3001** — contracts_backend exposed on 8001, contracts_frontend on 3001; nginx uses `host.docker.internal` for both
- **No companies/users management UI** in contracts_frontend — admin management via Django admin panel only
- **Fresh migrations** — don't copy facturation's migrations; generate clean initial migrations for contracts DB
- **Facturation domain rename** — facturation moves from bare `elbouazzatiholding.ma` / `api.elbouazzatiholding.ma` to `facturation.elbouazzatiholding.ma` / `facturation_api.elbouazzatiholding.ma`; requires env + nginx update before deploying contracts
- **`www.elbouazzatiholding.ma` reserved** — root domain is kept for a future portal; no app should claim it; a placeholder block returns 200 in the interim
- **SSL cert** — wildcard `*.elbouazzatiholding.ma` must cover all subdomains; ensure the cert also covers bare `elbouazzatiholding.ma` and `www.elbouazzatiholding.ma`
