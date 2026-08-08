// ui.js — DOM helpers. No fetch calls in here.

const $ = (id) => document.getElementById(id);

const STATUS_BADGE = {
  present: "text-emerald-700 bg-emerald-50 border-emerald-200",
  absent:  "text-rose-700 bg-rose-50 border-rose-200",
  flagged: "text-amber-700 bg-amber-50 border-amber-200",
  unknown: "text-slate-600 bg-slate-100 border-slate-200",
};

const STATUS_DOT = {
  present: "bg-emerald-500",
  absent:  "bg-rose-500",
  flagged: "bg-amber-500",
  unknown: "bg-slate-400",
};

const escapeHtml = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]),
  );

function statusPill(status) {
  const cls = STATUS_BADGE[status] || STATUS_BADGE.unknown;
  const dot = STATUS_DOT[status] || STATUS_DOT.unknown;
  return `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md border text-[11px] font-medium uppercase tracking-wide ${cls}">
            <span class="w-1.5 h-1.5 rounded-full ${dot}"></span>${escapeHtml(status)}
          </span>`;
}

function showBanner(message, type = "error") {
  const b = $("banner");
  const icon =
    type === "error"
      ? `<svg class="w-4 h-4 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m0 3v.008M12 3l9 15.75H3L12 3z"/></svg>`
      : `<svg class="w-4 h-4 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4M12 22a10 10 0 100-20 10 10 0 000 20z"/></svg>`;
  const cls =
    type === "error"
      ? "bg-rose-50 text-rose-800 border border-rose-200"
      : "bg-emerald-50 text-emerald-800 border border-emerald-200";
  b.className = `max-w-7xl mx-auto mt-4 px-4 py-3 rounded-lg text-sm flex items-center gap-2 ${cls}`;
  b.innerHTML = `${icon}<span>${escapeHtml(message)}</span>`;
  b.classList.remove("hidden");
  clearTimeout(showBanner._t);
  showBanner._t = setTimeout(() => b.classList.add("hidden"), 4500);
}

function setProcessLoading(isLoading) {
  $("processBtn").disabled = isLoading;
  $("processSpinner").classList.toggle("hidden", !isLoading);
  $("processIcon").classList.toggle("hidden", isLoading);
  $("processStatus").textContent = isLoading ? "Processing…" : "";
}

// ------------------------------- KPI cards -------------------------------

const KPI_ICONS = {
  students: `<svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.75" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z"/></svg>`,
  sessions: `<svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.75" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5"/></svg>`,
  records:  `<svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.75" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>`,
  rate:     `<svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.75" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 3v18h18M8 17V9m4 8v-5m4 5V6"/></svg>`,
};

function kpiCard({ label, value, icon, tint }) {
  return `
    <div class="rounded-2xl border border-slate-200 bg-white p-4 flex items-center gap-3 shadow-sm hover:shadow-md hover:border-brand-200 transition-all">
      <div class="w-10 h-10 rounded-xl ${tint} grid place-items-center flex-shrink-0">${icon}</div>
      <div class="flex-1 min-w-0">
        <div class="text-[10px] font-semibold uppercase tracking-widest text-slate-500">${escapeHtml(label)}</div>
        <div class="text-2xl font-semibold text-slate-900 font-mono leading-tight truncate">${escapeHtml(value)}</div>
      </div>
    </div>`;
}

function renderKpiStrip(a) {
  $("kpiStrip").innerHTML = [
    kpiCard({ label: "Students", value: a.total_students,             icon: KPI_ICONS.students, tint: "bg-brand-50 text-brand-500" }),
    kpiCard({ label: "Sessions", value: a.total_sessions,             icon: KPI_ICONS.sessions, tint: "bg-brand-50 text-brand-500" }),
    kpiCard({ label: "Records",  value: a.total_records,              icon: KPI_ICONS.records,  tint: "bg-brand-50 text-brand-500" }),
    kpiCard({ label: "Rate",     value: a.overall_attendance_rate + "%", icon: KPI_ICONS.rate,  tint: "bg-accent-50 text-accent-600" }),
  ].join("");
}

// ------------------------------- Stages -------------------------------

function renderStages(stages) {
  const grid = $("stagesGrid");
  grid.innerHTML = "";
  Object.entries(stages).forEach(([label, url], i) => {
    grid.insertAdjacentHTML("beforeend", `
      <figure class="group text-center">
        <a href="${url}" target="_blank" class="block rounded-lg border border-slate-200 overflow-hidden bg-slate-50 hover:shadow-md hover:border-brand-200 transition-all">
          <div class="aspect-[3/4] overflow-hidden">
            <img src="${url}" alt="${escapeHtml(label)}"
                 class="w-full h-full object-contain group-hover:scale-[1.02] transition-transform"
                 loading="lazy" />
          </div>
        </a>
        <figcaption class="mt-2 text-[11px] text-slate-500 flex items-center justify-center gap-1.5">
          <span class="font-mono text-slate-400">${String(i + 1).padStart(2, "0")}</span>
          <span class="capitalize">${escapeHtml(label)}</span>
        </figcaption>
      </figure>`);
  });
  $("stages").classList.remove("hidden");
}

// ------------------------------- Results -------------------------------

function renderResults(subject, results) {
  $("subjectMeta").textContent = `${subject.code} · ${subject.title || ""} · ${subject.date || ""}`;

  const body = $("resultsBody");
  body.innerHTML = "";
  const counts = { present: 0, absent: 0, flagged: 0 };
  results.forEach((r) => {
    counts[r.status] = (counts[r.status] || 0) + 1;
    body.insertAdjacentHTML("beforeend", `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="p-3 text-slate-400 font-mono">${r.no}</td>
        <td class="p-3 font-mono text-brand-600">${escapeHtml(r.index)}</td>
        <td class="p-3">${escapeHtml(r.name)}</td>
        <td class="p-3">${statusPill(r.status)}</td>
        <td class="p-3 font-mono text-xs text-slate-500">${r.score ?? "—"}</td>
      </tr>`);
  });

  $("resultsSummary").innerHTML = `
    <span class="font-medium text-slate-700">${results.length}</span> students ·
    <span class="text-emerald-700">${counts.present} present</span> ·
    <span class="text-rose-700">${counts.absent} absent</span> ·
    <span class="text-amber-700">${counts.flagged} flagged</span>`;

  $("results").classList.remove("hidden");
}

// ------------------------------- Visualize -------------------------------

function renderChart(url) {
  $("chartWrap").innerHTML = `
    <img src="${url}" alt="Attendance chart" class="max-w-full rounded-lg"
         onerror="this.parentNode.innerHTML='<p class=&quot;text-xs text-rose-500&quot;>Could not load chart. Save some sessions first.</p>'"/>`;
}

// ------------------------------- Investigate -------------------------------

function renderVerify(data) {
  $("verifyEmpty").classList.add("hidden");
  const box = $("verifyResult");
  const cls = STATUS_BADGE[data.status] || STATUS_BADGE.unknown;
  const scoreLine = data.score != null
    ? `<div class="text-xs text-slate-500 mt-1">Match score <span class="font-mono text-slate-800">${data.score}</span></div>`
    : "";
  const dateLine = data.date
    ? `<div class="text-xs text-slate-500 mt-1">Last session <span class="font-mono text-slate-800">${escapeHtml(data.date)}</span></div>`
    : "";
  const nameLine = data.name
    ? `<div class="text-sm font-medium text-slate-900">${escapeHtml(data.name)} <span class="font-mono text-xs text-slate-400">${escapeHtml(data.index)}</span></div>`
    : `<div class="text-sm font-mono text-slate-700">${escapeHtml(data.index)}</div>`;

  box.innerHTML = `
    <div class="rounded-lg border ${cls} p-4">
      ${nameLine}
      <div class="mt-2">${statusPill(data.status)}</div>
      ${scoreLine}
      ${dateLine}
      <div class="text-xs text-slate-600 mt-3">${escapeHtml(data.message || "")}</div>
    </div>`;
  box.classList.remove("hidden");
}

// ------------------------------- Analytics -------------------------------

function renderAnalytics(a) {
  renderKpiStrip(a);

  const sessionBody = $("perSessionBody");
  sessionBody.innerHTML = a.per_session.length
    ? a.per_session.map((s) => {
        const rate = s.attendance_rate;
        const rateCls = rate >= 80 ? "text-emerald-700" : rate >= 50 ? "text-amber-700" : "text-rose-700";
        return `
          <tr class="hover:bg-slate-50 transition-colors">
            <td class="p-2.5 font-mono text-slate-700">${escapeHtml(s.date)}</td>
            <td class="p-2.5 text-emerald-700 font-mono">${s.present}</td>
            <td class="p-2.5 text-rose-700 font-mono">${s.absent}</td>
            <td class="p-2.5 text-amber-700 font-mono">${s.flagged}</td>
            <td class="p-2.5 font-mono font-medium ${rateCls}">${rate}%</td>
          </tr>`;
      }).join("")
    : `<tr><td colspan="5" class="p-6 text-center text-xs text-slate-400">No sessions saved yet.</td></tr>`;

  const absBody = $("topAbsenteesBody");
  absBody.innerHTML = a.top_absentees.length
    ? a.top_absentees.map((s) => `
        <tr class="hover:bg-slate-50 transition-colors">
          <td class="p-2.5 font-mono text-brand-600">${escapeHtml(s.student_idx)}</td>
          <td class="p-2.5">${escapeHtml(s.name)}</td>
          <td class="p-2.5 font-mono text-rose-700 font-medium">${s.absent_count}</td>
        </tr>`).join("")
    : `<tr><td colspan="3" class="p-6 text-center text-xs text-slate-400">No absences recorded yet.</td></tr>`;
}

// ------------------------------- Students roster -------------------------------

let _rosterSelected = null;

function renderRoster(students, onSelect) {
  const wrap = $("rosterWrap");
  const empty = $("rosterEmpty");
  if (!students.length) {
    wrap.classList.add("hidden");
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");
  wrap.classList.remove("hidden");

  const body = $("rosterBody");
  body.innerHTML = students.map((s) => {
    const selected = _rosterSelected === s.student_idx;
    return `
      <tr data-idx="${escapeHtml(s.student_idx)}"
          class="cursor-pointer transition-colors ${selected ? "bg-brand-50" : "hover:bg-slate-50"}">
        <td class="p-3 font-mono text-brand-600">${escapeHtml(s.student_idx)}</td>
        <td class="p-3">${escapeHtml(s.name)}</td>
        <td class="p-3 text-slate-400">
          <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
          </svg>
        </td>
      </tr>`;
  }).join("");

  body.querySelectorAll("tr[data-idx]").forEach((tr) => {
    tr.addEventListener("click", () => {
      _rosterSelected = tr.getAttribute("data-idx");
      body.querySelectorAll("tr[data-idx]").forEach((r) =>
        r.classList.toggle("bg-brand-50", r === tr),
      );
      onSelect(_rosterSelected);
    });
  });
}

function renderStudentAttendance(index, records, name) {
  $("rosterDetailEmpty").classList.add("hidden");
  $("rosterDetail").classList.remove("hidden");

  $("rosterDetailHead").innerHTML = `
    <div class="flex items-center justify-between">
      <div>
        <div class="text-sm font-medium text-slate-900">${escapeHtml(name || "")}</div>
        <div class="text-xs font-mono text-slate-500">${escapeHtml(index)}</div>
      </div>
      <span class="text-xs text-slate-500">${records.length} records</span>
    </div>`;

  const body = $("rosterDetailBody");
  body.innerHTML = records.length
    ? records.map((r) => `
        <tr class="hover:bg-slate-50 transition-colors">
          <td class="p-2.5 font-mono text-slate-700">${escapeHtml(r.date ?? "—")}</td>
          <td class="p-2.5 font-mono text-slate-500">${escapeHtml(r.subject_code ?? "—")}</td>
          <td class="p-2.5">${statusPill(r.status)}</td>
          <td class="p-2.5 font-mono text-xs text-slate-500">${r.match_score ?? "—"}</td>
        </tr>`).join("")
    : `<tr><td colspan="4" class="p-6 text-center text-xs text-slate-400">No attendance recorded for this student yet.</td></tr>`;
}
