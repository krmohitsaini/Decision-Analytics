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
else, run FLASK_PORT=5050 python app.py
```

Backend URL:

```text
http://localhost:5000/api/health
http://localhost:5050/api/health - on mac as 5000 is for AirPlay

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

- No database, Excel file, Oracle, Databricks, authentication, or analytics code is included yet.
- The frontend uses `VITE_API_BASE_URL` when provided, otherwise it defaults to `http://localhost:5000`.
