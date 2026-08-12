# Third-Party Notices

VOIDWEN's behavioral rules are adapted (rewritten from scratch, not copied) from
two upstream projects. No source code, SKILL.md, or command files from either
project were copied into this repository. Only the behavioral rule *ideas* were
reimplemented in original wording. The license texts below are reproduced as
required by each project's license.

VOIDWEN adapts **only the MIT-licensed prose/skill behavior** of caveman. It does
**not** use, link, or reimplement any code from caveman's engine directories
(`engine/`, `proxy/`, `mcp/`, `shrink/`, `browse/`, the cavemem Go core,
`shared/platform/`), which are covered by the Business Source License 1.1.

---

## ponytail

- Source: https://github.com/DietrichGebert/ponytail
- License: MIT
- Adapted for: VOIDWEN Layer 2 (code minimalism / YAGNI ladder)

```
MIT License

Copyright (c) 2026 DietrichGebert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## caveman

- Source: https://github.com/JuliusBrussee/caveman
- License: MIT (skill/prose half) + Business Source License 1.1 (engine dirs — NOT used by VOIDWEN)
- Adapted for: VOIDWEN Layer 1 (prose compression)

The MIT half (which is all VOIDWEN adapts):

```
MIT License

Copyright (c) 2026 Julius Brussee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

The engine directories are additionally covered by BSL-1.1. VOIDWEN does not
touch them, so BSL terms do not apply to this repository. Verify the upstream
`LICENSING.md` / `LICENSE.BSL` before adapting any engine behavior.
