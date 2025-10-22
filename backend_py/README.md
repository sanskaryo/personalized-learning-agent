# FastAPI Backend (Gemini + Supabase)

## Setup

1. Create virtual environment and install requirements
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r backend_py/requirements.txt
```

2. Copy env example and fill values
```bash
copy backend_py\.env.example .env  # Windows
# or
cp backend_py/.env.example .env     # Linux/Mac
```

Required values:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY` (or `SUPABASE_SERVICE_ROLE_KEY`)
- `GEMINI_API_KEY`

3. Run the server
```bash
uvicorn backend_py.main:app --reload --port 8000
```

## Endpoints
- `GET /health`
- `POST /api/chat/send` (auth required)
- `POST /api/progress/session/start` (auth required)
- `PUT /api/progress/session/{session_id}/end` (auth required)
- `GET /api/progress/stats` (auth required)

## Supabase Tables
Create these tables:

- `chat_messages`
  - `id: uuid default uuid_generate_v4()`
  - `user_id: uuid`
  - `role: text` ("user" | "assistant")
  - `content: text`
  - `session_id: uuid`
  - `created_at: timestamp with time zone default now()`

- `study_sessions`
  - `id: uuid`
  - `user_id: uuid`
  - `subject: text null`
  - `started_at: timestamp with time zone`
  - `ended_at: timestamp with time zone null`
  - `duration_seconds: int4 default 0`
