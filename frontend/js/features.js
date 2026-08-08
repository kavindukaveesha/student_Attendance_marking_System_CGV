// features.js — Feature Sandbox page. One handler per F1..F5 module.

// --------------- shared helpers ---------------

function thumb(url, label) {
  return `
    <figure class="text-center">
      <a href="${url}" target="_blank" class="block rounded-lg border border-slate-200 overflow-hidden bg-slate-50 hover:shadow-md hover:border-brand-200 transition-all">
        <img src="${url}" alt="${label}" loading="lazy" class="w-full object-contain aspect-[3/4]" />
      </a>
      <figcaption class="mt-1.5 text-[11px] text-slate-500 capitalize">${label}</figcaption>
    </figure>`;
}

function metric(label, value, tint = "bg-slate-100 text-slate-700") {
  return `
    <div class="rounded-lg border border-slate-200 bg-white p-3">
      <div class="text-[10px] font-semibold uppercase tracking-widest text-slate-500">${label}</div>
      <div class="mt-1 inline-block px-2 py-0.5 rounded ${tint} font-mono text-sm">${value}</div>
    </div>`;
}

function jsonBlock(obj) {
  return `<pre class="mt-3 text-[11px] bg-slate-900 text-slate-100 p-3 rounded-lg overflow-x-auto">${
    JSON.stringify(obj, null, 2)
  }</pre>`;
}

function busy(el, isBusy) {
  el.disabled = isBusy;
  el.classList.toggle("opacity-60", isBusy);
  el.textContent = isBusy ? "Running…" : el.dataset.label;
}

function cacheLabel(btn) {
  if (!btn.dataset.label) btn.dataset.label = btn.textContent;
}

// --------------- F1 --------------- image preprocessing
const f1Run = $("f1Run"); cacheLabel(f1Run);
f1Run.addEventListener("click", async () => {
  const file = $("f1File").files[0];
  if (!file) return showBanner("Choose an image first.");
  busy(f1Run, true);
  try {
    const d = await apiF1Preview(file);
    $("f1Out").innerHTML = `
      <div class="grid grid-cols-3 gap-3">
        ${thumb(d.original,  "original")}
        ${thumb(d.greyscale, "greyscale")}
        ${thumb(d.smoothed,  "smoothed")}
      </div>`;
  } catch (e) { showBanner(e.message); }
  finally { busy(f1Run, false); }
});

// --------------- F2 --------------- geometric correction
const f2Run = $("f2Run"); cacheLabel(f2Run);
f2Run.addEventListener("click", async () => {
  const file = $("f2File").files[0];
  if (!file) return showBanner("Choose an image first.");
  busy(f2Run, true);
  try {
    const d = await apiF2Deskew(file);
    $("f2Out").innerHTML = `
      <div class="grid md:grid-cols-3 gap-3 mb-3">
        ${metric("Detected angle", d.detected_angle_degrees + "°", "bg-accent-50 text-accent-700")}
        <div class="md:col-span-2"></div>
      </div>
      <div class="grid grid-cols-3 gap-3">
        ${thumb(d.original, "input")}
        ${thumb(d.deskewed, "deskewed")}
        ${thumb(d.resized,  "resized")}
      </div>`;
  } catch (e) { showBanner(e.message); }
  finally { busy(f2Run, false); }
});

// --------------- F3 --------------- table & cell segmentation
const f3Run = $("f3Run"); cacheLabel(f3Run);
f3Run.addEventListener("click", async () => {
  const file = $("f3File").files[0];
  const n = parseInt($("f3Num").value, 10) || 6;
  if (!file) return showBanner("Choose an image first.");
  busy(f3Run, true);
  try {
    const d = await apiF3Cells(file, n);
    const cellGrid = d.cells.map((u, i) => thumb(u, `cell ${i + 1}`)).join("");
    $("f3Out").innerHTML = `
      <div class="grid md:grid-cols-3 gap-3 mb-4">
        ${metric("Requested", d.num_students_requested)}
        ${metric("Extracted", d.cells_extracted, "bg-accent-50 text-accent-700")}
        <div>${thumb(d.binary, "binary")}</div>
      </div>
      <h4 class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Extracted cells</h4>
      <div class="grid grid-cols-3 md:grid-cols-6 gap-3">${cellGrid}</div>`;
  } catch (e) { showBanner(e.message); }
  finally { busy(f3Run, false); }
});

// --------------- F4 --------------- signature detection
const f4Run = $("f4Run"); cacheLabel(f4Run);
f4Run.addEventListener("click", async () => {
  const file = $("f4File").files[0];
  if (!file) return showBanner("Choose a cell image first.");
  busy(f4Run, true);
  try {
    const d = await apiF4Check(file);
    const tint = d.signed ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700";
    $("f4Out").innerHTML = `
      <div class="grid md:grid-cols-3 gap-3">
        ${metric("Ink ratio", d.ink_ratio)}
        ${metric("Threshold", d.threshold)}
        ${metric("Verdict", d.status.toUpperCase(), tint)}
      </div>
      ${jsonBlock(d)}`;
  } catch (e) { showBanner(e.message); }
  finally { busy(f4Run, false); }
});

// --------------- F5 --------------- signature recognition
const f5Run = $("f5Run"); cacheLabel(f5Run);
f5Run.addEventListener("click", async () => {
  const sample = $("f5Sample").files[0];
  const reference = $("f5Reference").files[0];
  if (!sample || !reference) return showBanner("Choose both a sample and a reference.");
  busy(f5Run, true);
  try {
    const d = await apiF5Compare(sample, reference);
    const tint = d.matched ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700";
    $("f5Out").innerHTML = `
      <div class="grid md:grid-cols-3 gap-3">
        ${metric("Similarity score", d.score)}
        ${metric("Threshold", d.threshold)}
        ${metric("Verdict", d.verdict.toUpperCase(), tint)}
      </div>
      ${jsonBlock(d)}`;
  } catch (e) { showBanner(e.message); }
  finally { busy(f5Run, false); }
});
