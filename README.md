# PayAndTimeManager

## Local Installation

Install the required Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the app

Start the local FastAPI server:

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Open the frontend in your browser:

```text
http://127.0.0.1:8000
```

## Storage

The app now stores data in a local SQLite database at `backend/data/app.db`.

## Demo data

Use curl to create a worker, record hours, then generate payslips.

```powershell
Set-Content -Path payload.json -Value '{"name":"Sally","role":"Gardener","hourly_rate":28.79}'
curl.exe -i -X POST http://127.0.0.1:8000/api/workers -H "Content-Type: application/json" --data-binary "@payload.json"
Remove-Item payload.json
```

```powershell
Set-Content -Path payload.json -Value '{"worker_id":"<worker-id>","date":"2026-05-21","start_time":"08:00","end_time":"16:00","notes":"Demo shift"}'
curl.exe -i -X POST http://127.0.0.1:8000/api/time-entries -H "Content-Type: application/json" --data-binary "@payload.json"
Remove-Item payload.json
```

```powershell
curl.exe http://127.0.0.1:8000/api/payslips
```

## Backend API tests

Check the worker list:

```powershell
curl http://127.0.0.1:8000/api/workers
```

Create a test worker:

```powershell
curl -X POST http://127.0.0.1:8000/api/workers ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Sam Serious\",\"role\":\"Gardener\",\"hourly_rate\":28.79}"
```

Generate payslips:

```powershell
curl http://127.0.0.1:8000/api/payslips
```tm

## Frontend test steps

1. Open `http://127.0.0.1:8000` in your browser.
2. Add a worker using the form.
3. Record time entries for that worker.
4. Add deductions if needed.
5. Generate the payslip preview.

## Notes

- The backend import issue with `No module named 'app'` is fixed by using package-relative imports in `backend/app/main.py`.
- Run the server from the project root so `backend.app.main` resolves correctly.
 
