# YouTube Transcript Tool

Paste a YouTube URL → get a clean, copyable transcript. Raw captions come
from `youtube-transcript-api` (free, no key); a fast Groq pass
(`whisper-large-v3`) restores punctuation/paragraphs. Per-request token
usage and cost print to the backend terminal.

## Project structure

```
backend/
  configs/    settings.py        env vars, Groq model + pricing table, CORS
  service/    youtube_service.py  low-level YouTube caption integration
              groq_service.py     low-level Groq call + cost math
  feature/    transcript_feature.py  combines the two services into the
                                     "build a transcript" use case
  api/        schemas.py          pydantic request/response contracts
  pipeline/   transcript_pipeline.py  runs the feature as a timed, logged
                                      step; shapes the API response
  routes/     transcript_routes.py    thin FastAPI routes, no logic
  main.py     app entry point, CORS + router wiring
  requirements.txt
  .env.example

frontend/
  src/
    api/        client.js, transcriptApi.js   raw fetch calls to the backend
    service/    transcriptService.js          validation + response shaping
    hooks/      useTranscript.js              React state (loading/error/data)
    components/ UrlInputForm, TranscriptPanel, CopyButton, MetaBar, ErrorMessage
    layouts/    MainLayout.jsx                 page shell
    pages/      HomePage.jsx                   composes everything above
    routes/     AppRoutes.jsx                  react-router-dom routes
    App.jsx, main.jsx, index.css
  package.json, vite.config.js, index.html
  .env.example
```

Request flow: `routes` → `pipeline` → `feature` → `service` (YouTube +
Groq). Each layer only knows about the one below it — routes never touch
services directly, and services never know about HTTP.

On the frontend: `pages` compose `components`, driven by `hooks`, which
call `service` (validation/shaping), which calls `api` (raw HTTP).

## Setup

**Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# edit .env and set GROQ_API_KEY
uvicorn main:app --reload --port 8000
```

**Frontend**
```bash          
cd frontend
npm install
cp .env.example .env   # points VITE_API_BASE_URL at the backend
npm run dev
```
Open the URL Vite prints (usually http://localhost:5173).

## Security note

Rotate any Groq key that's ever been pasted into a chat, ticket, or shared
doc — treat it as compromised. The backend reads the key only from `.env`
(gitignored), never from source, and the frontend never touches the key at all.

## Terminal logging

Every transcript request prints a line like:
```
[dQw4w9WgXcQ] model=llama-3.1-8b-instant prompt_tokens=812 completion_tokens=798 total_tokens=1610 cost=$0.000104 time=1.84s
```
Pricing lives in `backend/configs/settings.py` (`PRICING` dict) — Groq's
published rate for `llama-3.1-8b-instant` is $0.05/1M input tokens,
$0.08/1M output tokens as of July 2026. Check https://groq.com/pricing
periodically since rates change.

## Speed target (4-5s)

- Uses `llama-3.1-8b-instant`, Groq's fastest hosted model.
- Send `"use_llm_cleanup": false` in the request body to skip the Groq call
  entirely and get the raw (punctuation-light) captions almost instantly.
- Very long videos are truncated to `MAX_INPUT_CHARS` before the LLM pass
  to keep the call fast; the response flags `"truncated": true`.

## Known limitations

- `youtube-transcript-api` uses YouTube's public timedtext endpoints — no
  official SLA, and YouTube can rate-limit or block by IP if hit hard.
- Videos with captions disabled, or that are private/region-locked, return
  a clear 422 error instead of a transcript.
- Not affiliated with or authorized by YouTube; respect YouTube's Terms of
  Service for whatever you build on top of this.
