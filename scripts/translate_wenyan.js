#!/usr/bin/env node
// Wenyan -> English translation, terminal/CLI version.
//
// Two-hop chain, split across two runtimes:
//   hop1: wenyan -> modern Chinese   -- Python subprocess (hop1_wenyan_to_modern.py).
//         Required because this model is a BERT2BERT EncoderDecoderModel, and
//         transformers.js's model registry does not support the generic
//         "encoder-decoder" model_type -- confirmed by hand: loading it via
//         AutoModelForSeq2SeqLM in Node throws "Unsupported model type:
//         encoder-decoder". Don't "fix" this by trying dtype/device options;
//         it's an architecture the JS library doesn't implement, not a config
//         issue.
//   hop2: modern Chinese -> English  -- native Node, via @huggingface/transformers.
//         Xenova/opus-mt-zh-en is a MarianMT model, which IS supported natively.
//
// Usage (wenyan text is illustrative only -- pass real Classical Chinese as an
// argument or via stdin; no CJK literals appear in this source file itself,
// per this repo's Core Principle 3.1 -- see tests/test_skill.py):
//   node scripts/translate_wenyan.js "<wenyan text>"
//   echo "<wenyan text>" | node scripts/translate_wenyan.js
//   node scripts/translate_wenyan.js --verbose "..."   # show the modern-zh bridge step too
//
// Requires Python 3 with `transformers` + `torch` installed (same environment
// used for model/clean/*.py during dataset prep) available on PATH as
// `python3` (or `python` on Windows -- both are tried).

import { pipeline } from "@huggingface/transformers";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HOP1_SCRIPT = path.join(__dirname, "hop1_wenyan_to_modern.py");
const HOP2_MODEL_ID = "Xenova/opus-mt-zh-en";

function splitSentences(text) {
  return text
    .split(/(?<=[。！？.!?])/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function runPython(script, inputLines) {
  return new Promise((resolve, reject) => {
    // try python3 first (mac/linux convention), fall back to python (common on Windows)
    const candidates = process.platform === "win32" ? ["python", "python3"] : ["python3", "python"];
    tryNext(0);

    function tryNext(i) {
      if (i >= candidates.length) {
        reject(new Error("No Python interpreter found (tried: " + candidates.join(", ") + "). Install Python 3 with `pip install transformers torch` and ensure it's on PATH."));
        return;
      }
      const proc = spawn(candidates[i], [script], { stdio: ["pipe", "pipe", "inherit"] });
      let out = "";
      let spawnFailed = false;

      proc.on("error", () => {
        spawnFailed = true;
        tryNext(i + 1);
      });
      proc.stdout.on("data", (chunk) => { out += chunk.toString("utf-8"); });
      proc.on("close", (code) => {
        if (spawnFailed) return; // already handled via 'error'
        if (code !== 0) {
          reject(new Error(`hop1 (${candidates[i]} ${script}) exited with code ${code}`));
          return;
        }
        resolve(out.split("\n").map((l) => l.trim()).filter(Boolean));
      });

      proc.stdin.write(inputLines.join("\n") + "\n");
      proc.stdin.end();
    }
  });
}

async function wenyanToModern(sentences) {
  process.stderr.write("[hop1] wenyan -> modern Chinese (Python subprocess)...\n");
  return runPython(HOP1_SCRIPT, sentences);
}

async function modernToEnglish(sentences) {
  process.stderr.write("[hop2] modern Chinese -> English (Node, native)...\n");
  const translate = await pipeline("translation", HOP2_MODEL_ID);
  const outputs = await translate(sentences, { max_length: 256 });
  return outputs.map((o) => o.translation_text);
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf-8").trim();
}

async function main() {
  const args = process.argv.slice(2);
  const verbose = args.includes("--verbose") || args.includes("-v");
  const textArg = args.filter((a) => !a.startsWith("-")).join(" ").trim();

  const text = textArg || (!process.stdin.isTTY ? await readStdin() : "");
  if (!text) {
    console.error("Usage: translate_wenyan.js [--verbose] \"wenyan text\"");
    console.error("   or: echo \"wenyan text\" | translate_wenyan.js");
    process.exit(1);
  }

  const sentences = splitSentences(text);

  const modern = await wenyanToModern(sentences);
  if (modern.length !== sentences.length) {
    console.error(`Warning: hop1 returned ${modern.length} lines for ${sentences.length} input sentences -- output may be misaligned.`);
  }
  const english = await modernToEnglish(modern);

  if (verbose) {
    sentences.forEach((wenyan, i) => {
      console.log(`wenyan:  ${wenyan}`);
      console.log(`modern:  ${modern[i] ?? "(missing)"}`);
      console.log(`english: ${english[i] ?? "(missing)"}`);
      console.log();
    });
  } else {
    console.log(english.join(" "));
  }
}

main().catch((err) => {
  console.error(`Translation failed: ${err.message}`);
  process.exit(1);
});
