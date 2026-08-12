// Wenyan detection via Unicode codepoint arithmetic.
// No CJK character literals appear here (VOIDWEN Core Principle 3.1); every Chinese
// character is referenced by codepoint. Runs in the browser and under node (ESM).

const CJK_START = 0x4e00;
const CJK_END = 0x9fff;
const CJK_EXT_A_START = 0x3400;
const CJK_EXT_A_END = 0x4dbf;

const WENYAN_CJK_RATIO_THRESHOLD = 0.4;
const MIN_CONTENT_CHARS = 4;

export function isCjkCodepoint(codepoint) {
  return (
    (codepoint >= CJK_START && codepoint <= CJK_END) ||
    (codepoint >= CJK_EXT_A_START && codepoint <= CJK_EXT_A_END)
  );
}

// Strip fenced and inline code so code is never treated as translatable text.
export function stripCodeBlocks(text) {
  return text.replace(/```[\s\S]*?```/g, "").replace(/`[^`]+`/g, "");
}

// CJK density alone: wenyan has no inter-word spaces, so a whitespace-based
// average-token-length gate would always reject it. Ratio is the correct signal.
export function detectWenyan(text) {
  const content = stripCodeBlocks(text);
  if (content.length < MIN_CONTENT_CHARS) return false;

  let cjkCount = 0;
  for (const ch of content) {
    if (isCjkCodepoint(ch.codePointAt(0))) cjkCount++;
  }
  return cjkCount / content.length > WENYAN_CJK_RATIO_THRESHOLD;
}
