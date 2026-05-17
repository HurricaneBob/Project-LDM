# LDM — AI Leadership Simulation

Backend (Flask) + React frontend (`Project-LDM-feature-julyatpark-phase2`). Deterministic trust/cohesion/stabilization from communication signals; Gemini for narrative via [llm/prompts/](llm/prompts/) templates and [data/llm_call_schemas.json](data/llm_call_schemas.json).

## Quick start (Windows, no Docker)

**Terminal A — backend**

```powershell
cd Project-LDM
copy .env.example .env
# Edit .env: set GEMINI_API_KEY and LLM_MOCK=0 for live Gemini
.\run.ps1
```

Chat uses `client.models.generate_content()` in [`app.py`](app.py) (`call_gemini_json`), with prompts built from [`data/seed_scenarios.json`](data/seed_scenarios.json) and [`data/llm_call_schemas.json`](data/llm_call_schemas.json). Parameter updates remain deterministic via `SignalEngine` after each user message.

**Security:** Never paste API keys into source code. Use `.env` only. If a key was ever committed to `app.py`, revoke it in [Google AI Studio](https://aistudio.google.com/apikey) and create a new one.

**Terminal B — frontend**

```powershell
cd Project-LDM-feature-julyatpark-phase2
npm install
npm run dev
```

Open http://localhost:5173. With empty `VITE_API_BASE_URL`, Vite proxies `/api` to Flask on **port 5000**.

For production builds, set `VITE_API_BASE_URL` to your API origin (e.g. `http://localhost:5000`).

### Manual backend (no run.ps1)

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py init-db
.\.venv\Scripts\python.exe manage.py seed --force
.\.venv\Scripts\python.exe app.py
```

`GET /health` returns `{ "status": "ok", "llm": "live"|"mock" }` for LLM mode.

## APIs

| Endpoint | Purpose |
|----------|---------|
| `POST /api/chat` | **Frontend** — `{ sessionId, message, history }` |
| `POST /api/scenario/init` | Legacy scenario init |
| `POST /api/scenario/interact` | Legacy interact loop |
| `POST /api/evaluation/final` | Holistic evaluation |
| `GET /health` | Health check |

## LLM call types (schemas)

Defined in `data/llm_call_schemas.json`:

1. `1_game_init` — first scenario brief  
2. `2_scenario_init` — scenarios 2–5  
3. `3A_semantic_analysis` — communication signals (backend applies math)  
4. `3B_dialogue_generation` — persona lines  
5. `4_scenario_summary` / `5_holistic_summary` — wrap-up  

## Tests

```powershell
$env:LLM_MOCK="1"
.\.venv\Scripts\pytest
```

### Manual smoke test (full stack)

1. Backend: set `GEMINI_API_KEY` and `LLM_MOCK=0` in `.env`, run `.\run.ps1`.
2. Confirm `GET http://localhost:5000/health` returns `"llm": "live"` (or `"mock"` if no key).
3. Frontend: `cd Project-LDM-feature-julyatpark-phase2 && npm run dev`.
4. Login → onboarding → Chat: send a message; verify persona replies in Network tab (`POST /api/chat`).
5. Send a second message; confirm the same `sessionId` is reused.
6. Open Analysis with an active server session; holistic evaluation loads when `serverId` is set.
7. Remove `GEMINI_API_KEY` and restart backend; logs should warn and `/health` shows `"llm": "mock"`.

## Google Cloud deployment

### 1. Containerize API

```bash
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT/ldm/api:latest
```

Uses [Dockerfile](Dockerfile) (`gunicorn` on port 8080).

### 2. Cloud Run

```bash
gcloud run deploy ldm-api \
  --image REGION-docker.pkg.dev/PROJECT/ldm/api:latest \
  --set-secrets=GEMINI_API_KEY=gemini-key:latest \
  --set-env-vars=DATABASE_URL=postgresql+psycopg2://...,CPB_PATH=/app/Conceptual-Personality-Builder \
  --allow-unauthenticated
```

Bundle [Conceptual-Personality-Builder](https://github.com/Airam2W/Conceptual-Personality-Builder) in the image or set `CPB_PATH`.

### 3. Cloud SQL (PostgreSQL)

Create Postgres 16; set `DATABASE_URL`. Run once:

```bash
python manage.py init-db
python manage.py seed --force
```

Use [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-run) from Cloud Run.

### 4. Frontend (Firebase Hosting or Cloud Storage)

```bash
cd Project-LDM-feature-julyatpark-phase2
# Set to your Cloud Run URL
$env:VITE_API_BASE_URL="https://ldm-api-xxxxx.run.app"
npm run build
firebase deploy --only hosting
```

Enable CORS on Flask for your hosting origin (already `*` on `/api/*` for MVP).

### 5. Secret Manager

Store `GEMINI_API_KEY`; reference in Cloud Run. Never commit `.env`.

### 6. CI/CD (optional)

Cloud Build: `pytest` → build image → deploy Run → build frontend with `VITE_API_BASE_URL` → deploy Hosting.

### Cost tips

- `gemini-2.0-flash` for 3A/3B; eval model only for call type 5  
- `LLM_MOCK=1` in CI only  
- Cloud Run min instances 0  

## CPB

Set `CPB_PATH` to Conceptual-Personality-Builder root. Personalities seeded in `data/seed_scenarios.json` (commander, facilitator, strategist, supporter, adaptive).
