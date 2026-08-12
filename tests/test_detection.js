// Unit tests for the wenyan detector. Run: node tests/test_detection.js
// Chinese test inputs are built with String.fromCodePoint — no CJK literals here.
import assert from "node:assert";
import { detectWenyan, stripCodeBlocks, isCjkCodepoint } from "../web/detector.js";

const cjk = (...cps) => String.fromCodePoint(...cps);

// Classical-looking passage (codepoints only).
const wenyan = cjk(0x5b50, 0x66f0, 0x5b78, 0x800c, 0x6642, 0x4e60, 0x4e4b, 0x4e0d, 0x4ea6, 0x8aaa);
assert.strictEqual(detectWenyan(wenyan), true, "pure CJK passage should detect");

// English prose must not detect.
assert.strictEqual(detectWenyan("The Master said: to learn and practice in time."), false);

// Code fences are stripped: CJK only inside a fence must not trigger.
const fenced = "```\n" + cjk(0x4e4b, 0x4e5f, 0x8005) + "\n```";
assert.strictEqual(detectWenyan(fenced), false, "CJK inside code fence must be ignored");
assert.strictEqual(stripCodeBlocks(fenced).trim(), "");

// Short strings are rejected.
assert.strictEqual(detectWenyan(cjk(0x4e4b)), false);

// Range check.
assert.strictEqual(isCjkCodepoint(0x4e00), true);
assert.strictEqual(isCjkCodepoint("a".codePointAt(0)), false);

console.log("test_detection OK");
