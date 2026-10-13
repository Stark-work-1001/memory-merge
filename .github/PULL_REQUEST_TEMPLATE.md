## What and why

## Checklist
- [ ] `python -m unittest discover -s tests` passes
- [ ] New behaviour has a test, and docs changed in the same PR
- [ ] No safety property weakened (review gate, screening, fail-closed judge, no silent egress, erasure claims) -- or the PR explains why in docs/DECISIONS.md
- [ ] If retrieval changed: `memory-merge eval` numbers before/after are in the PR, tuned on the dev split only
- [ ] If the schema changed: a migration with a test that upgrades a database written by the previous release
