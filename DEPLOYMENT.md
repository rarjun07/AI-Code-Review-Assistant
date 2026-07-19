# Deployment

This project deploys as two services:

- FastAPI backend on Render
- React/Vite frontend on Vercel

The Render Blueprint creates a PostgreSQL database and supplies its private
connection string to the backend automatically.

The free Render PostgreSQL plan is suitable for this mentor demonstration, but
it expires 30 days after creation. Upgrade it or move to a permanent PostgreSQL
provider before storing important data.

## Render backend

1. Push this repository to GitHub, GitLab, or Bitbucket.
2. In Render, create a Blueprint from the repository's `render.yaml` file.
3. Supply the secret values requested during Blueprint creation:
   - `HF_TOKEN`
   - `FRONTEND_URL`
   - `CORS_ORIGINS`
   - `RESEND_API_KEY`
   - `PASSWORD_RESET_FROM_EMAIL`
4. Initially set both frontend values to the final Vercel origin, without a
   trailing slash, for example `https://your-project.vercel.app`.
5. After deployment, verify `https://your-render-service.onrender.com/health`.

Render generates `SECRET_KEY`; never copy the development secret into
production.

Create a Resend account and verify the sender domain before setting
`PASSWORD_RESET_FROM_EMAIL`, for example
`AI Code Review <reset@your-domain.example>`. Production reset tokens are sent
through the Resend HTTPS API and are never included in the API response.

Uploaded Python source files are deleted immediately after analysis. The
analysis results and upload metadata remain in PostgreSQL, so the application
does not depend on Render's temporary filesystem.

The backend's `start.sh` runs `alembic upgrade head` before starting FastAPI.
This creates or upgrades the production tables using the versioned migrations
in `backend/alembic/versions`.

## Existing local database

The local database was originally created before Alembic was added. Do not run
the initial migration against that existing database because its tables already
exist. After confirming that it contains the current `users`, `uploaded_files`,
and `analysis_reports` columns, adopt it once with:

```bash
cd backend
alembic stamp head
```

New empty databases should use `alembic upgrade head` instead.

## Vercel frontend

1. Import the same repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Add `VITE_API_URL` with the public Render backend origin, without a trailing
   slash, for example `https://your-render-service.onrender.com`.
4. Deploy and verify that `/login`, `/register`, `/upload`, and `/reports` load
   when opened directly.

The `frontend/vercel.json` rewrite sends direct browser routes to React Router
instead of returning a Vercel 404 page.
