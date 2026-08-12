// Wenyan -> English translation in the browser via transformers.js.
// Loads the ONNX int8 model from HuggingFace once; the service worker caches it so
// later sessions are instant and work offline. Zero server, zero API, zero tokens.

import { pipeline } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3";

const MODEL_ID = "CSV0ID/voidwen-opus-mt";

let translatorPromise = null;

// Memoized: the 80MB model loads at most once per session.
export function getTranslator(onProgress) {
  if (!translatorPromise) {
    translatorPromise = pipeline("translation", MODEL_ID, {
      dtype: "q8",
      progress_callback: onProgress,
    });
  }
  return translatorPromise;
}

// Split on sentence-ending punctuation (CJK and ASCII) via codepoints, no literals.
export function splitSentences(text) {
  return text
    .split(/(?<=[。！？.!?])/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export async function translateWenyan(text, onProgress) {
  const translate = await getTranslator(onProgress);
  const sentences = splitSentences(text);
  const outputs = await translate(sentences, { max_length: 256 });
  return outputs.map((o) => o.translation_text).join(" ");
}
