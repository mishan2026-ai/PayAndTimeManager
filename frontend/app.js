const API = {
  workers: "/api/workers",
  timeEntries: "/api/time-entries",
  deductions: "/api/deductions",
  payslips: "/api/payslips",
};

function fetchJson(url, options = {}) {
  return fetch(url, options).then((res) => {
    if (!res.ok) throw new Error(res.statusText || "Request failed");
    return res.json();
  });
}

async function loadWorkers() {
  const workers = await fetchJson(API.workers);
  const workerList = document.getElementById("worker-list");
  const timeWorker = document.getElementById("time-worker");
  const deductionWorker = document.getElementById("deduction-worker");
  workerList.innerHTML = "";
  timeWorker.innerHTML = "";
  deductionWorker.innerHTML = "";

  workers.forEach((worker) => {
    const card = document.createElement("div");
    card.className = "card-item";
    card.innerHTML = `
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="text-lg font-semibold">${worker.name}</p>
          <p class="text-sm text-slate-600">${worker.role}</p>
        </div>
        <span class="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">R${worker.hourly_rate.toFixed(2)}/hr</span>
      </div>
      <div class="mt-4 grid gap-2 sm:grid-cols-3">
        <div class="text-sm text-slate-600">Leave accrued: ${worker.leave_accrued.toFixed(1)}d</div>
        <div class="text-sm text-slate-600">Status: ${worker.active ? "Active" : "Inactive"}</div>
      </div>
    `;
    workerList.appendChild(card);

    const optionTime = document.createElement("option");
    optionTime.value = worker.id;
    optionTime.textContent = worker.name;
    timeWorker.appendChild(optionTime);

    const optionDed = document.createElement("option");
    optionDed.value = worker.id;
    optionDed.textContent = worker.name;
    deductionWorker.appendChild(optionDed);
  });
}

async function loadRecentEntries() {
  const workerId = document.getElementById("time-worker").value;
  if (!workerId) return;
  const entries = await fetchJson(`${API.timeEntries}?worker_id=${workerId}`);
  const recent = document.getElementById("recent-entries");
  recent.innerHTML = entries.length
    ? entries
        .slice(-5)
        .reverse()
        .map(
          (entry) => `
        <div class="card-item">
          <div class="flex items-center justify-between gap-3">
            <div>
              <p class="font-semibold">${entry.date}</p>
              <p class="text-sm text-slate-600">${entry.start_time} – ${entry.end_time}</p>
            </div>
            <span class="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">${entry.hours.toFixed(2)}h</span>
          </div>
          <p class="mt-2 text-sm text-slate-500">${entry.notes ?? "No notes"}</p>
        </div>`
        )
        .join("")
    : `<div class="rounded-3xl border border-slate-200 bg-slate-50 p-4 text-slate-600">No recent time entries.</div>`;
}

async function renderPayslips(month) {
  const period = month || document.getElementById("payslip-period").value;
  const url = period ? `${API.payslips}?month=${period}` : API.payslips;
  const payslips = await fetchJson(url);
  const preview = document.getElementById("payslip-preview");
  preview.innerHTML = payslips.length
    ? payslips
        .map(
          (item) => `
      <div class="card-item">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p class="text-lg font-semibold">${item.worker.name}</p>
            <p class="text-sm text-slate-600">${item.worker.role}</p>
            <p class="text-sm text-slate-600">Period: ${item.period}</p>
          </div>
          <div class="space-y-1 text-right">
            <p class="text-sm">Gross: R${item.gross_pay.toFixed(2)}</p>
            <p class="text-sm">UIF: R${item.uif.toFixed(2)}</p>
            <p class="text-sm">Deductions: R${item.deduction_total.toFixed(2)}</p>
            <p class="text-lg font-semibold">Net: R${item.net_pay.toFixed(2)}</p>
          </div>
        </div>
        <div class="mt-4 grid gap-3 sm:grid-cols-2">
          <div class="rounded-3xl bg-slate-50 p-4 text-sm text-slate-700">
            <p>Total hours: ${item.total_hours.toFixed(2)}</p>
            <p>Overtime: ${item.overtime_hours.toFixed(2)}</p>
            <p>Leave accrued: ${item.leave_accrued.toFixed(2)} days</p>
          </div>
          <div class="rounded-3xl bg-slate-50 p-4 text-sm text-slate-700">
            <p class="font-semibold mb-2">Time entries</p>
            ${item.time_entries.length
              ? item.time_entries
                  .slice(-3)
                  .map((entry) => `<p>${entry.date}: ${entry.hours.toFixed(2)}h</p>`)
                  .join("")
              : "No time entries recorded."}
          </div>
        </div>
      </div>`
        )
        .join("")
    : `<div class="rounded-3xl border border-slate-200 bg-slate-50 p-4 text-slate-600">No payslips available.</div>`;
}

async function handleSubmit(event, url, data, resetForm = null) {
  try {
    event.preventDefault();
    await fetchJson(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (resetForm) resetForm();
    await loadWorkers();
    await loadRecentEntries();
    await renderPayslips();
  } catch (error) {
    alert(error.message);
  }
}

function resetWorkerForm() {
  document.getElementById("worker-name").value = "";
  document.getElementById("worker-role").value = "Domestic worker";
  document.getElementById("worker-rate").value = "28.79";
}

function resetTimeForm() {
  document.getElementById("time-date").value = new Date().toISOString().slice(0, 10);
  document.getElementById("time-start").value = "08:00";
  document.getElementById("time-end").value = "17:00";
  document.getElementById("time-notes").value = "";
}

function resetDeductionForm() {
  document.getElementById("deduction-description").value = "";
  document.getElementById("deduction-amount").value = "";
}

async function init() {
  document.getElementById("worker-form").addEventListener("submit", async (event) => {
    await handleSubmit(event, API.workers, {
      name: document.getElementById("worker-name").value,
      role: document.getElementById("worker-role").value,
      hourly_rate: Number(document.getElementById("worker-rate").value),
    }, resetWorkerForm);
  });

  document.getElementById("time-form").addEventListener("submit", async (event) => {
    await handleSubmit(event, API.timeEntries, {
      worker_id: document.getElementById("time-worker").value,
      date: document.getElementById("time-date").value,
      start_time: document.getElementById("time-start").value,
      end_time: document.getElementById("time-end").value,
      notes: document.getElementById("time-notes").value,
    }, resetTimeForm);
  });

  document.getElementById("deduction-form").addEventListener("submit", async (event) => {
    await handleSubmit(event, API.deductions, {
      worker_id: document.getElementById("deduction-worker").value,
      description: document.getElementById("deduction-description").value,
      amount: Number(document.getElementById("deduction-amount").value),
    }, resetDeductionForm);
  });

  document.getElementById("payslip-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    await renderPayslips(document.getElementById("payslip-period").value);
  });

  document.getElementById("refresh-button").addEventListener("click", async () => {
    await loadWorkers();
    await loadRecentEntries();
    await renderPayslips();
  });

  document.getElementById("time-worker").addEventListener("change", loadRecentEntries);

  resetWorkerForm();
  resetTimeForm();

  await loadWorkers();
  await loadRecentEntries();
  await renderPayslips();
}

window.addEventListener("DOMContentLoaded", init);
