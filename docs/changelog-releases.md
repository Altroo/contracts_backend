# Contracts releases

The first numbered release under this convention is **2.12.0** (9 October 2026).
The prior package value, 0.1.0, was a scaffold value. Neither repository had release
 tags. Historical versions are reconstructed from 219 commits across both
repositories and 48 development dates; these dates do not prove deployment dates.

`changelog-history-sources.json` records each repository, full commit hash, date,
subject, body and changed files. Its versioning section explains the major
milestones: the initial contract application is 1.0.0; the dedicated subcontracting
workflow starts 2.0.0. Subsequent capabilities increment minor versions and
corrections/maintenance increment patches. The bilingual daily entries are in
`ws/migrations/data/0004_changelog_history.json`.

The seed preserves existing administrator wording and publication state. The
2.12.0 entry is seeded as a draft and is published only after frontend health
checks. Saving an entry does not broadcast an update.

## Publishing

1. Choose the next package version and prepare bilingual changelog content.
2. Apply compatible backend migrations and deploy the backend before the frontend.
   The production post-receive hook rebuilds containers but **does not run migrations**;
   migrations must be run explicitly as part of the release.
3. Deploy the frontend and confirm `/api/app-version` returns the intended version
   with `Cache-Control: no-store`. Check container health and the actual screens.
4. Publish the changelog entry. Set the latest `WsMaintenanceState.version` to the
   healthy frontend version with maintenance off. Use `full_clean()` and `save()`;
   `QuerySet.update()` skips the websocket signal.
5. Verify maintenance HTTP state and the websocket announcement, then confirm all
   company, personal and production remote heads.

Tabs predating 2.12.0 need one normal refresh to acquire the update protocol.
Subsequent releases can prompt them without discarding unsaved work automatically.

## Verification

Use `contracts_backend.settings_release_test`, which selects an isolated SQLite
preview database and in-memory test database. The full suite includes PostgreSQL
full-text search: start a disposable local PostgreSQL cluster and set
`CONTRACTS_RELEASE_POSTGRES_PORT` to its port. Tests then create/drop only
`contracts_release_isolated_test`, with UTF-8 encoding.

```sh
DJANGO_SETTINGS_MODULE=contracts_backend.settings_release_test \
  CONTRACTS_RELEASE_POSTGRES_PORT=56439 .venv/bin/python -m pytest -q --no-cov
DJANGO_SETTINGS_MODULE=contracts_backend.settings_release_test \
  .venv/bin/python manage.py makemigrations --check --dry-run
```

On macOS, WeasyPrint may additionally need
`DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`.

Frontend checks: `NEXT_PUBLIC_DOMAIN_URL_PREFIX='' bun x jest --maxWorkers=4
--coverage=false`, `bun run lint`, and `bun run build`. Browser verification covers
staff/member navigation, both languages, 320/390 px mobile and desktop layouts,
server-rendered theme preference, unsaved input preservation, and update dismissal,
maintenance suppression, availability errors and route-preserving reloads.
