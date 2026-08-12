"""Repo guards. Run: python tests/test_skill.py

Two jobs:
1. Structure: the skill, its command, and the plugin manifest are present and valid.
2. Core Principle 3.1: no CJK character literal exists anywhere in tracked source.
   The whole repo must be CJK-free; Chinese lives only in runtime output and in the
   gitignored, HuggingFace-hosted corpus.
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCAN_EXT = {".py", ".js", ".ts", ".mjs", ".sh", ".md", ".json", ".yaml", ".yml",
            ".toml", ".css", ".html", ".ipynb", ".txt", ".tsv", ".csv"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", "onnx", "onnx-int8"}

CJK_RANGES = ((0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0xF900, 0xFAFF), (0x20000, 0x2A6DF))


def is_cjk(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in CJK_RANGES)


def tracked_files():
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if os.path.splitext(name)[1].lower() in SCAN_EXT:
                yield os.path.join(dirpath, name)


def test_structure() -> None:
    assert os.path.isfile(os.path.join(ROOT, "skills/voidwen/SKILL.md"))
    with open(os.path.join(ROOT, "skills/voidwen/SKILL.md"), encoding="utf-8") as fh:
        head = fh.read(400)
    assert head.startswith("---") and "name: voidwen" in head, "SKILL.md frontmatter missing"
    assert os.path.isfile(os.path.join(ROOT, "commands/voidwen.md"))
    with open(os.path.join(ROOT, ".claude-plugin/plugin.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    assert manifest["name"] == "voidwen"
    print("structure OK")


def test_no_cjk_in_source() -> None:
    offenders = []
    for path in tracked_files():
        try:
            with open(path, encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, 1):
                    for ch in line:
                        if is_cjk(ord(ch)):
                            offenders.append(f"{os.path.relpath(path, ROOT)}:{lineno}")
                            break
                    else:
                        continue
                    break
        except (UnicodeDecodeError, OSError):
            continue
    assert not offenders, "CJK literal found (violates Core Principle 3.1):\n" + "\n".join(offenders)
    print("no-CJK-in-source OK")


if __name__ == "__main__":
    test_structure()
    test_no_cjk_in_source()
    print("test_skill OK")
