# Privacy

## What the software does with your data

- Everything is stored locally in the data directory (`memory-merge doctor` shows where), in
  plaintext SQLite and Markdown. Protect it with OS permissions and full-disk encryption.
- Nothing is sent anywhere unless you configure a model server. Loopback servers are allowed; a
  remote server needs HTTPS and `MM_ALLOW_REMOTE=1`. Indexing sends memory text, recall sends queries,
  the judge receives pending memories. See docs/THREAT_MODEL.md (T3).
- Session archiving stores conversation transcripts (redacted for detected secrets) only if you set
  up the hook or import them.
- `forget` hides a memory from every index but keeps its text in the database; `purge` deletes it and
  its derived copies, with the limits listed in docs/OPERATIONS.md. Backups you made are not touched.
- Credential screening is pattern matching, not data-loss prevention.

## What the repository contains

Source, tests, documentation and a synthetic evaluation dataset. No personal data, real memories,
databases, model weights or credentials. The `.gitignore` excludes data directories, databases,
backups, `.env` and key files. Release archives are built from an allowlist and scanned for
machine-specific paths, emails, phone numbers and token patterns (`tools/release.py`); that scan is a
safety net, not a guarantee.
