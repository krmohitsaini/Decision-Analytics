# Decision Analytics POC

Minimum Flask + React project to confirm the backend/API/frontend structure works before adding real data connections or analytics logic.

For the broader application direction, see [PLAN.md](./PLAN.md).

## Project Structure

```text
backend/    Flask API
frontend/   Vite React UI
```

## Backend

```bash
cd backend
python3 -m venv .venv
py -m venv .venv -- on windows machine
source .venv/bin/activate
-- on windows machine - 
first - 
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
then - 
  .venv\Scripts\Activate
pip install -r requirements.txt

-- it'll run the backend on default port 5000
python app.py
else, run -
FLASK_PORT=5050 python app.py
```

Backend URL:

```text
http://localhost:5000/api/health
http://localhost:5050/api/health - on mac as 5000 is for AirPlay
http://localhost:5050/api/dashboard/summary

```

Dashboard filters are API-backed:

```text
http://localhost:5050/api/dashboard/summary?scope=current
http://localhost:5050/api/dashboard/summary?scope=all&channel=Digital&commodity=ELE
```

Deep-dive analysis pages are also API-backed:

```text
http://localhost:5050/api/analysis/retention
http://localhost:5050/api/analysis/commercial
http://localhost:5050/api/analysis/portfolio
http://localhost:5050/api/analysis/products
http://localhost:5050/api/analysis/digital
http://localhost:5050/api/analysis/agents
http://localhost:5050/api/analysis/quality
```

Expected response:

```json
{
  "message": "Backend is running",
  "status": "ok"
}
```

## Frontend

Open a second terminal:

```bash
cd frontend
-- on windows machine - 
first - 
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
then - 
npm install --verbose
-- if above one fails, try -
  npm config set strict-ssl false
  npm install --verbose
npm run dev
  or
  VITE_API_BASE_URL=http://localhost:5050 npm run dev
  
```

Frontend URL:

```text
http://localhost:5173
```

The page should show the backend status from the Flask API.

By default, the frontend expects the backend on port `5050` using the same host you used to open the UI:

```text
http://localhost:5173      -> calls http://localhost:5050
http://192.168.x.x:5173    -> calls http://192.168.x.x:5050
```

If your backend is running on a different port, start the frontend with:

```bash
VITE_API_BASE_URL=http://localhost:<backend-port> npm run dev
```

## If Port 5000 Is Already In Use

On macOS, port `5000` may already be used by AirPlay Receiver. You can either disable that service or run the backend on another port:

```bash
cd backend
FLASK_PORT=5050 python app.py
```

Then start the frontend with the matching API URL:

```bash
cd frontend
VITE_API_BASE_URL=http://localhost:5050 npm run dev
```

## Moving To Another Machine

After pushing to GitHub and pulling on the other machine:

1. Install backend dependencies from `backend/requirements.txt`.
2. Install frontend dependencies with `npm install`.
3. Start Flask on port `5000`.
4. Start Vite on port `5173`.
5. Open `http://localhost:5173` and confirm the backend status is visible.

## Notes

- The dashboard summary API currently reads `Dataset/synthetic_energy_customer_sites.csv` through a replaceable backend data-source adapter.
- Use `CUSTOMER_SITES_SOURCE=csv` for the current local CSV source. `CUSTOMER_SITES_CSV_PATH=/path/to/file.csv` can override the default file path.
- A `CUSTOMER_SITES_SOURCE=databricks` adapter placeholder is present so the later table connection can replace CSV access without changing the frontend API contract.
- No Oracle connection, Databricks connection implementation, authentication, or production analytics orchestration is included yet.
- The frontend uses `VITE_API_BASE_URL` when provided, otherwise it calls port `5050` on the same host used to open the UI.
