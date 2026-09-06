# CAP Advisor

CAP Advisor generates MHT-CET college preference lists from cutoff data and
shows a Top 5 visual comparison with placement metrics, recruiter information,
package data, ratings, and college images.

## Features

- Reach, Match, Safe, and Explore college classification.
- Top 5 comparison cards with campus images and placement visuals.
- Live refresh from configured official college websites.
- Per-college JSON cache so repeated requests do not scrape the same website.
- Verified snapshot fallback when an official site is unavailable.
- Optional AI comparison summary through Groq.

## Project layout

```text
backend/   FastAPI API, scraper, cache integration, and prediction service
frontend/  React + Vite interface
data/      Public processed cutoff and college data
ml/        Trained prediction models and feature code
```

## Local development

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
$env:PYTHONPATH = (Resolve-Path backend).Path
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. Set `VITE_API_BASE` when the API is not running
at `http://localhost:8000/api/v1`.

## College image and metrics cache

When a comparison is requested, the backend checks
`data/cache/college_metrics_cache.json` for each college. Fresh records are
returned immediately. Missing or expired records fetch the college's official
website and cache the resolved metrics and image URL. The default cache TTL is
24 hours.

Configure this with:

```text
COLLEGE_METRICS_CACHE_TTL_SECONDS=86400
COLLEGE_METRICS_CACHE_FILE=data/cache/college_metrics_cache.json
```

The cache directory is ignored by Git. It is runtime data and must not be
committed.

## Environment and security

Keep credentials in a local `.env` file. Never commit API keys, SMTP
passwords, database credentials, generated cache files, `node_modules`, or
build output. Only public processed data, source code, and lockfiles belong in
the repository.

## Validation

```powershell
python -m compileall backend
cd frontend
npm run lint
npm run build
```
