# Decision Analytics Architecture Plan

## Summary

Build the application in stages. The current project is only a smoke-test skeleton: Flask backend, React frontend, and one health API. The longer-term goal is a client-presentable analytics application that can start with local/static data and later move to Oracle, Databricks, scheduled refreshes, and production deployment.

## Target Architecture

- Use a monorepo with clear boundaries:
  - `backend/` for Flask APIs, auth, data loading, analysis orchestration, and result serving.
  - `frontend/` for the React dashboard UI.
  - `data/` for POC-only Excel, CSV, or static sample files.
  - `artifacts/` for generated cached analysis outputs during the POC.
- Keep the frontend independent from the data source.
  - React should call Flask APIs only.
  - React should not know whether the data came from Excel, Oracle, or Databricks.
- Keep analysis logic separate from API routes.
  - Flask routes should receive requests and return JSON.
  - Python analysis modules should handle calculations, transformations, KPIs, and insights.
- Use cached results for heavier work.
  - For the POC, cache generated outputs locally.
  - For production, move cached outputs to database tables or Databricks-managed result tables.

## Data And Analysis Flow

Initial POC flow:

```text
Excel / static file
  -> Python data loader
  -> Python analysis module
  -> cached result artifact
  -> Flask API
  -> React UI
```

Production flow:

```text
Oracle / Databricks
  -> scheduled refresh job
  -> Python / Databricks analysis layer
  -> governed result tables or cached outputs
  -> Flask or production API layer
  -> React UI
```

## Backend Plan

- Start with Flask because it is lightweight and fits the Python analytics workflow.
- Add a data-source abstraction before introducing real data connections.
  - First adapter: Excel or CSV.
  - Later adapters: Oracle and Databricks.
- Add API endpoints gradually:
  - `GET /api/health`
  - `GET /api/datasets`
  - `GET /api/analysis/summary`
  - `GET /api/analysis/details`
  - Optional POC-only: `POST /api/admin/refresh`
- Avoid running long analysis directly inside request handlers once real data is introduced.
- For production, move long-running work to scheduled refresh jobs.

## Frontend Plan

- Build an actual dashboard as the first useful screen.
- Suggested first dashboard sections:
  - KPI summary strip.
  - Filter controls.
  - Trend or comparison charts.
  - Detail table.
  - Insight or recommendation panel.
  - Refresh/status indicator.
- Keep the design professional, simple, and client-demo ready.
- Use API response contracts rather than hardcoding business logic in React.

## Deployment Direction

- Current phase:
  - Run locally on the developer machine.
  - Use static data or Excel when analytics work begins.
  - Push to GitHub and pull on another machine to validate portability.
- Later phase:
  - Move refresh and data access closer to Databricks.
  - Add proper secrets management.
  - Add production authentication.
  - Add logging, monitoring, and CI checks.

## Current Smoke-Test Scope

The current implementation intentionally includes only:

- Flask backend.
- One `/api/health` endpoint.
- Vite React frontend.
- One React page that calls the backend.
- Local run instructions.

It intentionally does not include:

- Oracle connection.
- Databricks connection.
- Excel ingestion.
- Authentication.
- Charts.
- Analytics calculations.
- Production deployment setup.

## Testing Strategy

- Smoke-test now:
  - Backend starts locally.
  - `/api/health` returns JSON.
  - Frontend starts locally.
  - Frontend displays backend status.
- Next phase:
  - Add tests for data loaders.
  - Add tests for analysis functions.
  - Add tests for API response shapes.
  - Add frontend loading, error, and success state checks.

## Assumptions

- The first meaningful version is a POC for client presentation.
- The app will initially run locally.
- Static files or Excel can be used before real database connectivity.
- Oracle and Databricks should be introduced through replaceable data-source adapters.
- Scheduled refresh is preferred for production.
- The architecture should stay simple now but leave room to grow.
