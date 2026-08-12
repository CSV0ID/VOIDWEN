// Tests the pure markdown-table builder in pipeline.js.
// Run: node tests/test_pipeline.js
// The doc converters need browser APIs + CDN libs and are not unit-tested here;
// this guards the one piece of non-trivial pure logic.
import assert from "node:assert";
import { rowsToMarkdownTable } from "../web/pipeline.js";

const md = rowsToMarkdownTable([
  ["a", "b"],
  [1, 2],
  ["pipe|here", 3],
]);
const lines = md.split("\n");

assert.strictEqual(lines[0], "| a | b |");
assert.strictEqual(lines[1], "| --- | --- |");
assert.strictEqual(lines[2], "| 1 | 2 |");
assert.ok(lines[3].includes("pipe\\|here"), "pipe must be escaped");

// Ragged rows pad to the widest row.
const ragged = rowsToMarkdownTable([["x"], ["y", "z"]]);
assert.strictEqual(ragged.split("\n")[0], "| x |  |");

console.log("test_pipeline OK");
