# Memory Merge

Local-first, single-user long-term memory for AI agents. Agents propose memories over MCP; you
review them; approved memories come back as cited evidence. SQLite is the source of truth, Markdown
is a readable mirror you can edit, and nothing leaves your machine unless you configure it to.

Version `0.2.0a1` (alpha) · MIT · [中文说明](README.zh-CN.md) · [Changelog](CHANGELOG.md)

## What it does

- **Capture with review.** Agents capture decisions, preferences, procedures, lessons and facts;
  everything an agent or a file supplies is *pending* until you approve it. An agent cannot approve
  its own memory.
- **Retrieval that works for Chinese, Japanese and mixed text.** A bigram analyzer on SQLite FTS5
  replaces 0.1's whitespace tokenizer; optional local embeddings (Qwen3-Embedding) add semantic and
  cross-lingual recall.
- **Cited evidence, not answers.** `memory_rag_context` returns memories fenced as quoted data with
  `[memory:id]` citations; your agent writes the answer.
- **Briefing and profile.** A compact start-of-task context: your preferences, things to avoid,
  decisions, lessons. All of it is assembled from stored text, with no model involved.
- **Documents and sessions.** Import Markdown, text, PDF, browser bookmarks and highlights with
  page/heading provenance; archive Claude Code sessions automatically via a hook.
- **Lifecycle.** Revisions (`supersedes`), archive, forget, purge, duplicate detection with
  corroboration counts, contradiction surfacing.
- **Operations.** Verified backups, a restore drill, automatic schema migrations with a backup first,
  `doctor`, a local mind-graph viewer with optional review mode.

## Quick start

Requires Python 3.11+ (with SQLite FTS5, as in python.org builds and major distributions).

```bash
git clone https://github.com/Stark-work-1001/memory-merge.git
cd memory-merge
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1      POSIX: . .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m pip install .
memory-merge doctor
```

Try it with synthetic data:

```bash
memory-merge --data ./demo-data demo
memory-merge --data ./demo-data recall --project demo "事务的真源是什么"
memory-merge --data ./demo-data briefing --project demo
memory-merge --data ./demo-data web --port 8765        # http://127.0.0.1:8765, project "demo"
```

Connect an agent (prints config for your interpreter and data directory; writes nothing):

```bash
memory-merge setup claude-code        # or claude-desktop, codex, cursor, generic
```

Then give the agent [integrations/AGENT_INSTRUCTIONS.md](integrations/AGENT_INSTRUCTIONS.md).
Review what it captured:

```bash
memory-merge queue --project myproject
memory-merge review --project myproject MEMORY_ID approve
memory-merge web --review             # or review in the browser
```

Without `--data`/`MM_DATA` the store lives in your platform data directory (`memory-merge doctor`
shows where). Docker: `docker build -t memory-merge-local .` then
`docker run -i --rm -v memory-merge-data:/data memory-merge-local`.

## Retrieval quality, measured

On `datasets/memory-eval-v1` (240 memories in Chinese, English, mixed and Japanese; 160 graded
queries; options chosen on the 64-query dev split, numbers below from the 96-query test split):

| | nDCG@10 | Recall@10 | queries with no result | p50 latency |
|---|---|---|---|---|
| 0.1 (published code) | 0.340 | 0.392 | 45.8% | 6-11 ms |
| 0.2 lexical (default, no model) | 0.649 | 0.754 | 0% | 4-7 ms |
| 0.2 with Qwen3-Embedding-0.6B (Q8_0, via Ollama) | 0.827 | 0.887 | 0% | 200-470 ms* |

\* dominated by the HTTP round trip to the embedding server on a shared GPU. Reproduce with the
commands in [docs/EVALUATION.md](docs/EVALUATION.md), which also covers the dataset's limits (it is
synthetic, written for this project) and per-query-type results. Lexical retrieval is not semantic:
paraphrases without shared words need the embedding stage.

## MCP tools

Every instance: `memory_capture`, `memory_remember`, `memory_recall`, `memory_rag_context`,
`memory_briefing`, `memory_profile`, `memory_graph`, `memory_judge`, `memory_index`,
`memory_session_search`, `memory_health`; `memory_import` when `MM_IMPORT_ROOT` is set.

Reviewer instance only (`MM_ENABLE_REVIEW=1`): `memory_review_queue`, `memory_review`,
`memory_review_document`, `memory_link`, `memory_link_remove`, `memory_judge_pending`,
`memory_purge`.

Errors are structured JSON with stable codes ([docs/DATA_FORMATS.md](docs/DATA_FORMATS.md#error-contract)).

## Configuration

Environment variables only (MCP hosts set them per server):

| Variable | Purpose |
|---|---|
| `MM_DATA` | data directory |
| `MM_ENABLE_REVIEW=1` | register review tools on this MCP instance |
| `MM_TRUST_AGENT_CONFIRM=1` | let `memory_remember(confirmed=True)` approve immediately (off by default) |
| `MM_IMPORT_ROOT` | enable `memory_import`, confined to this directory |
| `MM_EMBED_URL`, `MM_EMBED_MODEL`, `MM_EMBED_KEY`, `MM_EMBED_PRESET=qwen3-embedding`, `MM_EMBED_DIM`, `MM_EMBED_REVISION` | OpenAI-compatible embedding server (Ollama, llama.cpp, vLLM, LM Studio, TEI) |
| `MM_EMBED_BACKEND=sentence-transformers` or `llama-cpp`, `MM_EMBED_PATH` | in-process embeddings, no server |
| `MM_JUDGE_URL`, `MM_JUDGE_MODEL`, `MM_JUDGE_NO_THINK=1`, `MM_JUDGE_BACKEND`, `MM_JUDGE_PATH` | optional advisory judge |
| `MM_ALLOW_REMOTE=1` | permit non-loopback HTTPS providers and hub downloads |
| `MM_FUSION_LEXICAL_WEIGHT` | RRF weight of lexical results (default 0.01) |
| `MM_LOG_LEVEL` | stderr log level |

Full details: [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md), [docs/MODELS.md](docs/MODELS.md).

## Command line

```text
capture | remember | list | show | recall | rag | briefing | profile         memories
queue | review | judge | judge-calibration | link | unlink                   review
import | docs | sync [--watch] | session import|list|show|search|purge|hook    documents, mirror, sessions
index | prune-vectors                                                        embeddings
health | doctor | backup | restore | drill | rebuild | maintain | report | purge   operations
web [--review] | setup HOST | eval | demo | version
```

`memory-merge COMMAND --help` for options.

## Safety model in one paragraph

Retrieved memory is evidence, never instructions. Automatic capture is pending; only you approve.
The judge advises and fails closed. No network egress without explicit configuration. Single
memories with credentials are rejected; imports are redacted. `forget` hides; `purge` deletes and
compacts, but cannot reach existing backups, snapshots or remote providers. The full threat model,
including what is *not* defended, is in [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## What is not verified

CI is configured for Linux, macOS and Windows on Python 3.11-3.13 but has not run yet; the test suite
was run on Windows 11 (Python 3.11.15, 3.12.13, 3.13.5, 3.14.5). Retrieval numbers come from one
synthetic dataset. No load test; it is designed for one user. The llama.cpp in-process backends are
implemented against llama-cpp-python's documented API but were not executed (its build failed on the
test machine); see docs/MODELS.md for which model paths were executed. PDF import was tested on a
generated PDF only. Full list: [docs/EVALUATION.md](docs/EVALUATION.md#not-verified).

## Documentation

[Architecture](docs/ARCHITECTURE.md) · [Decisions](docs/DECISIONS.md) · [Threat model](docs/THREAT_MODEL.md) ·
[Models](docs/MODELS.md) · [Evaluation](docs/EVALUATION.md) · [Operations](docs/OPERATIONS.md) ·
[Integrations](docs/INTEGRATIONS.md) · [Data formats](docs/DATA_FORMATS.md) · [Native kernel](docs/NATIVE.md) ·
[Independent review](docs/REVIEW.md) · [References](docs/REFERENCES.md) · [Research notes](docs/RESEARCH.md) ·
[Releasing](docs/RELEASING.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Privacy](PRIVACY.md)

## Credits

Design ideas from 24 open-source memory projects, each listed with commit, license and what was
taken in [docs/REFERENCES.md](docs/REFERENCES.md). No code was copied from them.

## License

MIT, see [LICENSE](LICENSE) and [LICENSE-STATUS.md](LICENSE-STATUS.md).
