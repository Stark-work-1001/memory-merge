# License status / 许可状态

Memory Merge's original source code and documentation are licensed under the **MIT License**; see
[LICENSE](LICENSE). This is the license of record for every release since 0.1.0. (An earlier version
of this file, written before the license was chosen, said that no license had been selected; that
statement is obsolete.)

Memory Merge 的原创源码与文档采用 **MIT 许可证**（见 [LICENSE](LICENSE)），自 0.1.0 起所有发布均以此为准。
本文件早先写于选定许可证之前，其中“尚未选择许可证”的说法已经失效。

The MIT license covers only Memory Merge's own work:

- Referenced projects keep their own copyright and licenses. No code from them is included; see
  [docs/REFERENCES.md](docs/REFERENCES.md) for each project, its license as published and what
  ideas were taken. Some references are copyleft (AGPL-3.0: Basic Memory, OpenViking), one has a
  non-commercial custom license (raya-ac/engram since 2026-09-19), and one declares conflicting
  licenses (edg-l/engram-mcp); verify the exact upstream version before reusing anything.
- Dependencies are installed separately and keep their own terms (the MCP Python SDK is MIT; PyO3 and
  maturin, used only to build the optional native kernel, are MIT OR Apache-2.0).
- Model weights are not distributed. The models used in measurements (Qwen3-Embedding-0.6B,
  Qwen3-1.7B) are Apache-2.0 on their official Hugging Face pages.
- `datasets/memory-eval-v1` was written for this project and is released under the same MIT license.

This is not legal advice.
