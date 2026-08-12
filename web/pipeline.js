// Document -> markdown, entirely in the browser. No server, no API, zero tokens.
// Libraries are loaded lazily from CDN only when a matching file arrives.
//
// voidwen: best-effort converters for the common case (standard business PDFs, Word
// docs, spreadsheets, web pages, simple images). Complex academic layouts, LaTeX,
// and multi-column scans are out of scope here — that is a server-side job (MinERU).

const CDN = {
  pdfjs: "https://cdn.jsdelivr.net/npm/pdfjs-dist@4/build/pdf.min.mjs",
  pdfWorker: "https://cdn.jsdelivr.net/npm/pdfjs-dist@4/build/pdf.worker.min.mjs",
  mammoth: "https://cdn.jsdelivr.net/npm/mammoth@1/mammoth.browser.min.js",
  xlsx: "https://cdn.jsdelivr.net/npm/xlsx@0.18.5/+esm",
  turndown: "https://cdn.jsdelivr.net/npm/turndown@7/+esm",
  tesseract: "https://cdn.jsdelivr.net/npm/tesseract.js@5/+esm",
};

function extOf(name) {
  return (name.split(".").pop() || "").toLowerCase();
}

async function htmlToMarkdown(html) {
  const { default: TurndownService } = await import(CDN.turndown);
  return new TurndownService().turndown(html);
}

async function pdfToMarkdown(buffer) {
  const pdfjs = await import(CDN.pdfjs);
  pdfjs.GlobalWorkerOptions.workerSrc = CDN.pdfWorker;
  const doc = await pdfjs.getDocument({ data: buffer }).promise;
  const pages = [];
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i);
    const content = await page.getTextContent();
    const text = content.items.map((it) => it.str).join(" ").trim();
    if (text) pages.push(text);
  }
  // No text layer -> scanned PDF; caller can retry via OCR.
  if (!pages.length) throw new Error("no text layer (scanned PDF) — use OCR");
  return pages.join("\n\n");
}

async function docxToMarkdown(buffer) {
  await import(CDN.mammoth); // attaches window.mammoth
  const { value: html } = await window.mammoth.convertToHtml({ arrayBuffer: buffer });
  return htmlToMarkdown(html);
}

async function xlsxToMarkdown(buffer) {
  const XLSX = await import(CDN.xlsx);
  const wb = XLSX.read(buffer, { type: "array" });
  const out = [];
  for (const name of wb.SheetNames) {
    const rows = XLSX.utils.sheet_to_json(wb.Sheets[name], { header: 1, blankrows: false });
    if (!rows.length) continue;
    out.push(`## ${name}\n`);
    out.push(rowsToMarkdownTable(rows));
  }
  return out.join("\n");
}

export function rowsToMarkdownTable(rows) {
  const cell = (v) => String(v ?? "").replace(/\|/g, "\\|");
  const width = Math.max(...rows.map((r) => r.length));
  const line = (r) => "| " + Array.from({ length: width }, (_, i) => cell(r[i])).join(" | ") + " |";
  const header = line(rows[0]);
  const sep = "| " + Array.from({ length: width }, () => "---").join(" | ") + " |";
  return [header, sep, ...rows.slice(1).map(line)].join("\n");
}

async function imageToMarkdown(blob) {
  const { createWorker } = await import(CDN.tesseract);
  const worker = await createWorker("eng"); // add languages as needed
  const { data } = await worker.recognize(blob);
  await worker.terminate();
  return data.text.trim();
}

// Convert a File/Blob to markdown. Returns a string.
export async function toMarkdown(file) {
  const ext = extOf(file.name || "");
  const type = file.type || "";

  if (ext === "html" || ext === "htm" || type.includes("html")) {
    return htmlToMarkdown(await file.text());
  }
  if (ext === "docx" || type.includes("wordprocessingml")) {
    return docxToMarkdown(await file.arrayBuffer());
  }
  if (ext === "xlsx" || ext === "xls" || ext === "csv" || type.includes("spreadsheet")) {
    return xlsxToMarkdown(new Uint8Array(await file.arrayBuffer()));
  }
  if (ext === "pdf" || type.includes("pdf")) {
    try {
      return await pdfToMarkdown(await file.arrayBuffer());
    } catch {
      return imageToMarkdown(file); // fall back to OCR for scanned PDFs
    }
  }
  if (type.startsWith("image/")) {
    return imageToMarkdown(file);
  }
  // Unknown type: treat as plain text.
  return (await file.text()).trim();
}
