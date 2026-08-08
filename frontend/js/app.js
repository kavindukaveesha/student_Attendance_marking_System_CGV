// app.js — wire buttons to api.js + ui.js.

let currentData = null;
let rosterCache = [];  // { student_idx, name }

// -------- 1 · PROCESS --------
$("processBtn").addEventListener("click", async () => {
  const sheet = $("sheet").files[0];
  const info = $("info").files[0];
  if (!sheet || !info) return showBanner("Please choose both a sheet image and info.xml.");

  setProcessLoading(true);
  try {
    currentData = await apiProcess(sheet, info);
    renderStages(currentData.stages);
    renderResults(currentData.subject, currentData.results);
    showBanner(`Processed ${currentData.results.length} students.`, "success");
    document.getElementById("results").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    showBanner(err.message);
  } finally {
    setProcessLoading(false);
  }
});

// -------- 3 · SAVE --------
$("saveBtn").addEventListener("click", async () => {
  if (!currentData) return showBanner("Process a sheet first.");
  $("saveStatus").textContent = "Saving…";
  try {
    const res = await apiSave({
      subject: currentData.subject,
      results: currentData.results,
    });
    $("saveStatus").textContent = `Saved ${res.saved} records.`;
    showBanner(`Saved ${res.saved} attendance records.`, "success");
    await refreshAnalytics();
    await refreshRoster();
  } catch (err) {
    $("saveStatus").textContent = "";
    showBanner(err.message);
  }
});

// -------- 4 · VISUALIZE --------
$("chartBtn").addEventListener("click", () => {
  const idx = $("chartIdx").value.trim();
  const kind = $("chartKind").value;
  if (!idx) return showBanner("Enter a student index.");
  renderChart(apiChartUrl(idx, kind));
});

// -------- 5 · INVESTIGATE --------
$("verifyBtn").addEventListener("click", async () => {
  const idx = $("verifyIdx").value.trim();
  if (!idx) return showBanner("Enter a student index.");
  try {
    const data = await apiInvestigate(idx);
    renderVerify(data);
  } catch (err) {
    showBanner(err.message);
  }
});

// -------- 6 · ANALYTICS --------
async function refreshAnalytics() {
  try {
    const data = await apiAnalytics();
    renderAnalytics(data);
  } catch (err) {
    showBanner(err.message);
  }
}
$("analyticsBtn").addEventListener("click", refreshAnalytics);

// -------- 7 · STUDENTS ROSTER --------
async function refreshRoster() {
  try {
    rosterCache = await apiStudents();
    renderRoster(rosterCache, async (idx) => {
      try {
        const records = await apiStudentAttendance(idx);
        const student = rosterCache.find((s) => s.student_idx === idx);
        renderStudentAttendance(idx, records, student?.name);
      } catch (err) {
        showBanner(err.message);
      }
    });
  } catch (err) {
    showBanner(err.message);
  }
}

// -------- initial load --------
(async () => {
  await refreshAnalytics();
  await refreshRoster();
})();
