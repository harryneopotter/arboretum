# Cloud Run Deployment

This backend is ready to deploy as a container on Google Cloud Run.

## Required env vars

- `QDRANT_URL`
- `QDRANT_API_KEY`
- `OPENAI_API_KEY`
- Optional:
  - `ADMIN_LOG_TOKEN`
  - `BETA_TELEMETRY_ENABLED`
- One of:
  - `DATABASE_URL`
  - `DB_USER`, `DB_PASS`, `DB_NAME`, `DB_HOST`

## Beta telemetry

- `BETA_TELEMETRY_ENABLED=true` keeps the app sending action logs to `/events`.
- `ADMIN_LOG_TOKEN` is required for `GET /events/admin`.
- If `ADMIN_LOG_TOKEN` is not set, `/events/admin` now returns `503`.
- A local admin dashboard is available at `admin/index.html`. Run `scripts/start-admin.ps1` and open `http://localhost:4173`.

## Recommended beta setup

- Cloud Run for the API
- Managed Postgres for persistence
- Public unauthenticated access for beta testing

## Build and deploy

From the repo root:

### Option 1: Use the helper script

```bash
bash scripts/deploy-cloudrun.sh
```

PowerShell:

```powershell
.\scripts\deploy-cloudrun.ps1
```

### Option 2: Run the command manually

```bash
gcloud run deploy arboretum-backend \
  --source backend \
  --region us-central1 \
  --allow-unauthenticated \
  --cpu 2 \
  --memory 2Gi \
  --timeout 300 \
  --add-cloudsql-instances soa1-485322:us-central1:my-pg-instance \
  --set-env-vars "QDRANT_URL=...,QDRANT_API_KEY=...,OPENAI_API_KEY=...,DB_USER=postgres,DB_PASS=...,DB_NAME=my_app_db,DB_HOST=/cloudsql/soa1-485322:us-central1:my-pg-instance,BETA_TELEMETRY_ENABLED=true"
```

## Notes

- The container listens on port `8080`.
- Local development still works without `DATABASE_URL`; it falls back to SQLite.
- `backend/arboretum.db` should not be used as the production database for Cloud Run.
- For Cloud SQL, either set `DATABASE_URL` or use the `DB_*` fields shown above.
- Keep the password out of git history and shell transcripts when possible.
- Beta telemetry is intentionally lightweight: it records action names, screen names, and response summaries, not raw secrets.
