# Jarvis

Jarvis is a React/Vite frontend backed by a FastAPI service. The frontend lives in `jarvis-frontend`, uses Vite's `/api` proxy during development, and keeps Groq credentials on the backend.

## Prerequisites

- Python 3.11+
- A Groq API key

## Install and run

```powershell
git clone https://github.com/Vijayendra06/doomsday.git
cd doomsday
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
Push-Location jarvis-frontend
npm install
Pop-Location
```

Edit `.env` and set `GROQ_API_KEY`. To run the backend and frontend together, use the combined launcher:

```powershell
.\run-fullstack.ps1
```

Open `http://localhost:1420`. The API binds to `127.0.0.1:8765` and is proxied by Vite, so browser requests use `/api` without a second CORS configuration.

To run either service separately:

```powershell
.\run-dev.ps1
Push-Location jarvis-frontend
npm run dev
Pop-Location
```

The frontend uses `VITE_DEMO_MODE=false` and `VITE_API_BASE_URL=/api` by default. For a deployed frontend, set `VITE_API_BASE_URL` to the backend's public `/api` URL at build time.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Required secret used for Groq chat and transcription. |
| `GROQ_CHAT_MODEL` | Optional Groq chat model override. |
| `JARVIS_BACKEND_HOST` / `JARVIS_BACKEND_PORT` | Local bind address and port. Keep the host loopback for workshop/local use. |
| `JARVIS_ALLOWED_ORIGINS` | Comma-separated exact frontend origins for CORS. Never use `*`. |
| `JARVIS_LOCAL_ACTIONS_ENABLED` | Defaults to `false`. Enables the four-app Windows allowlist only for a local browser. |

Never commit `.env`.

## API contracts

| Method and path | Request | Response | Purpose |
| --- | --- | --- | --- |
| `GET /api/health` | — | `{ "status": "ok" }` | Service health. |
| `POST /api/chat` | `{ "sessionId": "UUID", "text": "..." }` | `{ "sessionId": "UUID", "reply": "...", "turnsRetained": 0-6 }` | Groq chat with in-memory context. |
| `GET /api/voices` | — | `{ "voices": [{ "id", "label" }] }` | Edge TTS voice choices. |
| `POST /api/tts` | `{ "text": "...", "voiceId": "..." }` | `audio/mpeg` | Synthesized voice audio. |
| `POST /api/transcribe` | multipart field `audio` | `{ "transcript": "..." }` | Groq Whisper transcription. Audio is capped at 10 MB. |
| `POST /api/web-actions/plan` | `{ "text": "..." }` | `{ "kind", "label", "url" }` | Produces a constrained website/search destination for frontend confirmation. |
| `GET /api/local-actions/status` | — | `{ "enabled": boolean }` | Local bridge availability. |
| `POST /api/local-actions/plan` | `{ "text": "..." }` | `{ "kind", "appId", "label", "requiresConfirmation" }` | Plans one allowlisted app. |
| `POST /api/local-actions/execute` | `{ "appId": "...", "confirmed": true }` | `{ "ok": true, "message": "..." }` | Opens a fixed allowlisted Windows app. |

## Safety boundary

The planner can only produce browser websites/searches. The optional local bridge accepts only the IDs `calculator`, `notepad`, `file_explorer`, and `vscode`. It rejects non-local browser origins and does not accept arbitrary paths, program names, shell commands, arguments, or LLM-generated execution data.

## Tests

```powershell
cd backend
python -m pytest tests -q
```

For production, use a process manager appropriate to your Python host and set exact CORS origins. A public deployment must leave `JARVIS_LOCAL_ACTIONS_ENABLED=false`.
