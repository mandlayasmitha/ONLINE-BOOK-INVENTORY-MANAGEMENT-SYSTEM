# Venu Compiler

A full-stack educational code playground with Python execution, static complexity analysis, hybrid analysis, and benchmark visualization.

## Architecture

- React + TypeScript + Vite + Monaco + Recharts frontend
- FastAPI backend
- Python AST rule-based static analyzer
- Subprocess development execution adapter
- Docker/Compose deployment layout
- PostgreSQL configuration for persistence

The development executor is **not a security boundary**. Production execution must use a hardened Docker sandbox with non-root users, read-only filesystems, dropped capabilities, network disabled, PID limits, memory limits, CPU limits, output limits, and cleanup.

## Run locally

### Backend

```powershell
$env:Path += ";C:\Users\Mote Venu\AppData\Local\Programs\Python\Python312"
cd backend
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

The Python compiler runtime includes NumPy, pandas, requests, and SymPy. Use the package chips in the editor to insert the matching import statement.

### Frontend

```powershell
$env:Path = "C:\Program Files\nodejs;$env:Path"
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Docker

```powershell
docker compose up --build
```

Frontend: http://localhost:5173  
API: http://localhost:8000/docs

## Deploy

The React frontend is Vercel-ready. Import this repository in Vercel, set the root directory to `frontend`, add `VITE_API_URL` with the public backend URL, and deploy.

The FastAPI backend is not deployed securely by the static frontend deployment alone. Deploy `backend/` to a Docker-capable service and ensure code execution uses a hardened Docker sandbox rather than the development subprocess adapter.

## API

- `POST /api/execute`
- `POST /api/analyze/static`
- `POST /api/analyze/hybrid`
- `POST /api/benchmark`
- `GET /api/health`

## Tests

```powershell
cd backend
.venv\Scripts\python -m pytest -q
```

Frontend build:

```powershell
cd frontend
npm run build
```
