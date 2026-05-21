from __future__ import annotations
from datetime import date, datetime, time
from pydantic import BaseModel, Field, PositiveFloat
from typing import List, Optional

class WorkerBase(BaseModel):
    name: str = Field(..., min_length=1)
    role: str = Field(default="Domestic worker")
    hourly_rate: PositiveFloat = Field(default=28.79)
    start_date: Optional[date] = None

class WorkerCreate(WorkerBase):
    pass

class WorkerUpdate(WorkerBase):
    active: Optional[bool] = True

class Worker(WorkerBase):
    id: str
    active: bool = True
    leave_accrued: float = 0.0

class TimeEntryBase(BaseModel):
    worker_id: str
    date: date
    start_time: time
    end_time: time
    notes: Optional[str] = None

class TimeEntryCreate(TimeEntryBase):
    pass

class TimeEntry(TimeEntryBase):
    id: str
    hours: float

class DeductionBase(BaseModel):
    worker_id: str
    description: str = Field(..., min_length=1)
    amount: PositiveFloat
    monthly: bool = True

class DeductionCreate(DeductionBase):
    pass

class Deduction(DeductionBase):
    id: str

class PayslipSummary(BaseModel):
    worker: Worker
    period: str
    total_hours: float
    overtime_hours: float
    gross_pay: float
    uif: float
    deduction_total: float
    net_pay: float
    leave_accrued: float
    time_entries: List[TimeEntry]
    deductions: List[Deduction]
