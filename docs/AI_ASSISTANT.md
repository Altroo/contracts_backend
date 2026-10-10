# Contracts AI Assistant

Status: tested adapter; disabled by default pending shared-model acceptance. Application identifier: `contrat`.

## Setup and rollback

Install the existing requirements, including the reviewed vendored shared package. Preserve a private database backup using the established operator procedure before migrations. Run `python manage.py migrate chat_ai`, then `python manage.py sync_ai_knowledge`. The migration creates assistant tables; it does not change existing contract/account columns. Existing Docker startup does not run migrations automatically.

Keep `CHAT_AI_ASSISTANT_ENABLED=False` until model acceptance and activation authorization. At activation, supply `CHAT_AI_MODEL_URL`, `CHAT_AI_MODEL_ID` and `CHAT_AI_MODEL_KEY` through private runtime configuration for the existing shared Colibri service. Never publish these values or expose the raw inference server. Defaults: model timeout 120 seconds, maximum output 512 tokens, history retention 30 days. The adapter caps results at ten and queues no unbounded inference work.

Disable the feature flag to roll back the UI/API without altering contracts or deleting history. Preserve assistant tables and confirmed-operation audit records. Restore source through the normal Git release process. Do not drop database volumes or reverse confirmed business writes as a software rollback.

Run `python manage.py purge_ai_history` on the existing private scheduler: it removes expired conversation/pending data and old non-write audits, preserving confirmed-operation audit metadata. `sync_ai_knowledge` incrementally updates only approved EN/FR documents and rejects unsupported scope/sensitivity metadata.

## API and authorization

All `/api/ai/v1/` endpoints reuse native JWT authentication: capabilities; conversation create/list/retrieve/delete; messages (JSON or authenticated SSE); record selection; exact-action confirmation; feedback; scoped documents. Document query keys are `company_id`, `document_format` (`pdf`/`docx`) and `language` (`fr`/`en`). Native DRF reserves `format`, so it is not the document selector.

The company is chosen from the backend catalogue and bound to the conversation. Existing read/print/create/edit/delete flags and staff-only user administration are rechecked for every invocation and delivery. Model/browser IDs never grant permission. Cards are bounded and history re-fetches authorized records. Knowledge is filtered before retrieval; exact source versions are checked on replay. Pending writes expire after five minutes and validate owner, scope, current permissions, record/dependency fingerprint and a single explicit confirmation. The native mutation view owns business validation and history.

Tools: `search_records`, `get_record`, `navigate`, `knowledge`, `previous_results`, `contract_document`, `prepare_change`. No SQL, shell, arbitrary URLs, financial aggregation, permission changes or automatic writes are exposed. Contract HT/TVA/TTC values use native calculations; collected revenue/profit are unsupported because there is no authoritative ledger/report service.

## Verification and limits

Final local PostgreSQL suite: 576 tests plus 4 subtests, including authorization, company/history isolation, revocation, exact-target write confirmation, native audit, document scope and safe navigation. Local dummy browser checks cover selected-company reads, read-only denial, native PDF, card navigation/list return, confirmation and actor history, EN/FR history, mobile layout and overlay priority. No production records were used as fixtures.

The shared model's Contracts baseline, fine-tuning and >=95% selection/arguments acceptance are incomplete. UI/native-handler tests do not establish model accuracy. Production activation and natural-language model-driven acceptance must be reported separately.
