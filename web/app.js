// VOIDWEN browser app: doc -> markdown (to feed an agent), and wenyan -> English
// (to read the agent's compressed output). Both run fully client-side.

import { toMarkdown } from "./pipeline.js";
import { detectWenyan } from "./detector.js";
import { translateWenyan } from "./translator.js";

const $ = (id) => document.getElementById(id);

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js").catch(() => {});
}

// --- Document -> markdown ---
$("file").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  $("markdown").value = "Converting...";
  try {
    $("markdown").value = await toMarkdown(file);
  } catch (err) {
    $("markdown").value = `Conversion failed: ${err.message}`;
  }
});

// --- Wenyan -> English ---
$("translate").addEventListener("click", async () => {
  const text = $("response").value;
  const out = $("english");
  if (!detectWenyan(text)) {
    out.textContent = "Not detected as wenyan — displaying as-is.\n\n" + text;
    return;
  }
  out.textContent = "Loading model (first run downloads ~80MB, then cached)...";
  try {
    out.textContent = await translateWenyan(text, (p) => {
      if (p.progress != null) out.textContent = `Loading model: ${Math.round(p.progress)}%`;
    });
  } catch (err) {
    out.textContent = `Translation failed: ${err.message}\n\nRaw:\n${text}`;
  }
});
