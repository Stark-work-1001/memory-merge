# Memory Merge 0.2.0a1

> Alpha. Pre-release: mark it as such on GitHub. Not production-stable.

## Highlights

- **Retrieval that works for Chinese and mixed text.** On the project's labelled dataset (test split,
  96 queries): nDCG@10 0.340 (0.1) -> 0.649 with the new lexical analyzer, 0.827 with local
  Qwen3-Embedding-0.6B; queries returning nothing 45.8% -> 0%.
- **Agents can no longer approve their own memories**, and stored text can no longer forge evidence
  boundaries or citations.
- **Real deletion**: `purge` removes a memory and every derived copy, verified by scanning the data
  directory for the text afterwards.
- **Documents, sessions, two-way Markdown**: imports with citable provenance, a session archive with
  a Claude Code hook, and mirror edits turned into reviewable proposals.
- **Safe upgrades**: migrations refuse newer databases, take a verified backup first, and are tested
  against databases written by the real 0.1 code.
- **Model work, measured**: verified model files, immutable vector fingerprints with drift detection,
  tuned fusion, an optional Rust kernel (85-125x faster vector search), and a judge evaluation whose
  result is reported as found: a 1.7B judge is reliable in format (100% valid with thinking off) but weak in judgement (71% category agreement on held-out data after a prompt fix, poor injection detection), so it stays off by default.

## Upgrading

Back up, install, run `memory-merge doctor`; the first open migrates the database and writes its own
verified backup. Read "Upgrading from 0.1" in docs/OPERATIONS.md for behaviour changes.

## Not verified

CI has not run yet (tests passed on Windows 11 with Python 3.11-3.14); numbers come from one
synthetic dataset; no load test; llama.cpp backends were not executed; PDF import was tested on a generated PDF only. Full list in
docs/EVALUATION.md.

Full change list: CHANGELOG.md.
