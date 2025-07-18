# personal-notes-manager-fc8393c1

## Fullstack Personal Notes Application

This project consists of three containers:
- **notes_db**: PostgreSQL database container.
- **notes_backend**: FastAPI backend container for notes and user logic.
- **notes_frontend**: React web frontend container.

---

## Container Integration & Setup

### 1. Database (notes_db)
- Runs a PostgreSQL server.
- Exposes environment variables needed by the backend:
  - `POSTGRES_URL`: Full Postgres connection URI (`postgresql://user:password@host:port/db`)
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`
- Example URL (used by backend):  
  `postgresql://notes_user:notes_password@notes_db:5432/notes_db`

### 2. Backend API (notes_backend)
- FastAPI-based REST API.
- Reads DB configs from environment (see `.env.example`).
- Serves at:  
  `http://localhost:8000/` (default; change with `--host`/`--port`)
- Key endpoints:
  - `/api/auth/register` — Register user
  - `/api/auth/login` — Obtain JWT
  - `/api/notes/` — CRUD endpoints for notes (JWT required)
- Expects the following environment variables (see `.env.example`):
  - `POSTGRES_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`
  - (Optional) `SECRET_KEY` for JWT tokens
- Start backend with:
  ```bash
  uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
  ```
- The backend must have network access to the `notes_db` container at the hostname or network alias `notes_db`.

### 3. Frontend (notes_frontend)
- React app (see its container/README).
- Must be configured to send requests to backend (API URL):
  - Example: `REACT_APP_API_URL=http://localhost:8000/`
- Ensures CORS is enabled on backend for frontend origin.

---

## Running Locally (Dev-Oriented)

1. **Start notes_db container.**
    - Make sure the environment variables in `.env` or your Docker Compose match backend expectation.
2. **Copy and edit the backend `.env.example` to `.env`** in the `notes_backend` directory.
3. **Start backend server** (see above command).
4. **Start frontend** with the correct API URL set in its config.

---

## Example .env for Backend

See [`notes_backend/.env.example`](notes_backend/.env.example).

---

## Helpful Links

- **Backend OpenAPI docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend OpenAPI schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## Troubleshooting Tips

- Ensure all containers are on the same Docker/Docker Compose network.
- Verify the backend can reach the database at the configured host/port.
- Check CORS settings if API calls from frontend are blocked.