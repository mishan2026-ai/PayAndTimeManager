from __future__ import annotations
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from .schemas import (
    Deduction,
    DeductionCreate,
    PayslipSummary,
    TimeEntry,
    TimeEntryCreate,
    Worker,
    WorkerCreate,
    WorkerUpdate,
)
from .storage import get_collection, update_collection

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="PayAndTimeManager API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

UIF_RATE = 0.01
MIN_HOURLY_RATE = 28.79

@app.get("/", response_class=FileResponse)
def serve_frontend():
    return FRONTEND_DIR / "index.html"

@app.get("/api/workers", response_model=List[Worker])
def list_workers():
    return get_collection("workers")

@app.post("/api/workers", response_model=Worker)
def create_worker(payload: WorkerCreate):
    workers = get_collection("workers")
    worker = Worker(
        id=str(uuid4()),
        name=payload.name.strip(),
        role=payload.role.strip() or "Domestic worker",
        hourly_rate=payload.hourly_rate or MIN_HOURLY_RATE,
        start_date=payload.start_date,
        active=True,
        leave_accrued=0.0,
    )
    workers.append(worker.model_dump())
    update_collection("workers", workers)
    return worker

@app.put("/api/workers/{worker_id}", response_model=Worker)
def update_worker(worker_id: str, payload: WorkerUpdate):
    workers = get_collection("workers")
    for i, item in enumerate(workers):
        if item["id"] == worker_id:
            updated = {**item, **payload.model_dump(exclude_none=True)}
            workers[i] = updated
            update_collection("workers", workers)
            return Worker(**updated)
    raise HTTPException(status_code=404, detail="Worker not found")

@app.delete("/api/workers/{worker_id}")
def delete_worker(worker_id: str):
    workers = get_collection("workers")
    filtered = [w for w in workers if w["id"] != worker_id]
    if len(filtered) == len(workers):
        raise HTTPException(status_code=404, detail="Worker not found")
    update_collection("workers", filtered)
    return {"status": "deleted"}

@app.get("/api/time-entries", response_model=List[TimeEntry])
def list_time_entries(worker_id: Optional[str] = None):
    entries = get_collection("time_entries")
    if worker_id:
        entries = [entry for entry in entries if entry["worker_id"] == worker_id]
    return entries

@app.post("/api/time-entries", response_model=TimeEntry)
def create_time_entry(payload: TimeEntryCreate):
    workers = get_collection("workers")
    if not any(worker["id"] == payload.worker_id for worker in workers):
        raise HTTPException(status_code=404, detail="Worker not found")

    start = datetime.combine(payload.date, payload.start_time)
    end = datetime.combine(payload.date, payload.end_time)
    if end <= start:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    hours = round((end - start).seconds / 3600, 2)
    entry = TimeEntry(
        id=str(uuid4()),
        worker_id=payload.worker_id,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        notes=payload.notes,
        hours=hours,
    )
    entries = get_collection("time_entries")
    entries.append(entry.model_dump())
    update_collection("time_entries", entries)
    return entry

@app.get("/api/deductions", response_model=List[Deduction])
def list_deductions(worker_id: Optional[str] = None):
    deductions = get_collection("deductions")
    if worker_id:
        deductions = [d for d in deductions if d["worker_id"] == worker_id]
    return deductions

@app.post("/api/deductions", response_model=Deduction)
def create_deduction(payload: DeductionCreate):
    workers = get_collection("workers")
    if not any(worker["id"] == payload.worker_id for worker in workers):
        raise HTTPException(status_code=404, detail="Worker not found")
    deduction = Deduction(id=str(uuid4()), **payload.model_dump())
    deductions = get_collection("deductions")
    deductions.append(deduction.model_dump())
    update_collection("deductions", deductions)
    return deduction

@app.get("/api/payslips", response_model=List[PayslipSummary])
def generate_payslips(month: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}$")):
    workers = get_collection("workers")
    time_entries = get_collection("time_entries")
    deductions = get_collection("deductions")
    period = month or date.today().strftime("%Y-%m")
    year, month_num = map(int, period.split("-"))
    payslips: List[PayslipSummary] = []

    for worker_data in workers:
        worker = Worker(**worker_data)
        worker_entries = [TimeEntry(**entry) for entry in time_entries if entry["worker_id"] == worker.id]
        worker_entries = [entry for entry in worker_entries if entry.date.strftime("%Y-%m") == period]
        worker_deductions = [Deduction(**ded) for ded in deductions if ded["worker_id"] == worker.id]
        total_hours = sum(entry.hours for entry in worker_entries)
        overtime = max(0.0, total_hours - 45.0)
        gross = round(total_hours * worker.hourly_rate, 2)
        uif = round(gross * UIF_RATE, 2)
        deduction_total = round(sum(d.amount for d in worker_deductions), 2)
        net = round(gross - uif - deduction_total, 2)
        leave_accrued = round(total_hours / 9 / 17, 2)

        payslips.append(
            PayslipSummary(
                worker=worker,
                period=period,
                total_hours=round(total_hours, 2),
                overtime_hours=round(overtime, 2),
                gross_pay=gross,
                uif=uif,
                deduction_total=deduction_total,
                net_pay=net,
                leave_accrued=leave_accrued,
                time_entries=worker_entries,
                deductions=worker_deductions,
            )
        )
    return payslips
