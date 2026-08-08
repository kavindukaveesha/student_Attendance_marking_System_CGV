// api.js — the ONLY file that knows API endpoints.

const API = "";

async function apiProcess(sheetFile, infoFile) {
  const fd = new FormData();
  fd.append("image", sheetFile);
  fd.append("info", infoFile);
  const res = await fetch(`${API}/api/attendance/process`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`Process failed (${res.status}): ${await res.text()}`);
  return res.json();
}

async function apiSave(payload) {
  const res = await fetch(`${API}/api/attendance/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Save failed (${res.status}): ${await res.text()}`);
  return res.json();
}

function apiChartUrl(index, kind = "bar") {
  const t = Date.now();
  return `${API}/api/visualization/${encodeURIComponent(index)}?kind=${kind}&t=${t}`;
}

async function apiInvestigate(index) {
  const res = await fetch(`${API}/api/investigate/${encodeURIComponent(index)}`, { method: "POST" });
  if (!res.ok) throw new Error(`Investigate failed (${res.status})`);
  return res.json();
}

async function apiAnalytics() {
  const res = await fetch(`${API}/api/analytics/summary`);
  if (!res.ok) throw new Error(`Analytics failed (${res.status})`);
  return res.json();
}

async function apiStudents() {
  const res = await fetch(`${API}/api/students`);
  if (!res.ok) throw new Error(`Students failed (${res.status})`);
  return res.json();
}

async function apiStudentAttendance(index) {
  const res = await fetch(`${API}/api/students/${encodeURIComponent(index)}/attendance`);
  if (!res.ok) throw new Error(`Student attendance failed (${res.status})`);
  return res.json();
}

// ---------------- Per-feature demo endpoints (F1 – F5) ----------------

async function apiF1Preview(imageFile) {
  const fd = new FormData();
  fd.append("image", imageFile);
  const res = await fetch(`${API}/api/features/image-processing/preview`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`F1 preview failed (${res.status})`);
  return res.json();
}

async function apiF2Deskew(imageFile) {
  const fd = new FormData();
  fd.append("image", imageFile);
  const res = await fetch(`${API}/api/features/transforms/deskew`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`F2 deskew failed (${res.status})`);
  return res.json();
}

async function apiF3Cells(imageFile, numStudents) {
  const fd = new FormData();
  fd.append("image", imageFile);
  fd.append("num_students", String(numStudents));
  const res = await fetch(`${API}/api/features/table-extraction/cells`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`F3 cells failed (${res.status})`);
  return res.json();
}

async function apiF4Check(imageFile) {
  const fd = new FormData();
  fd.append("image", imageFile);
  const res = await fetch(`${API}/api/features/signature-detection/check`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`F4 check failed (${res.status})`);
  return res.json();
}

async function apiF5Compare(sampleFile, referenceFile) {
  const fd = new FormData();
  fd.append("sample", sampleFile);
  fd.append("reference", referenceFile);
  const res = await fetch(`${API}/api/features/signature-recognition/compare`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`F5 compare failed (${res.status})`);
  return res.json();
}
