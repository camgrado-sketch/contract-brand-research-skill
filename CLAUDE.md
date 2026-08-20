# Claude Code Project Instructions

Read and follow [AGENTS.md](AGENTS.md) as the repository-wide source of truth.

This repository deliberately maintains one shared Skill at `skills/contract-brand-research/`. Do not create a Claude-specific copy of the workflow. Claude-specific plugin metadata belongs only in `.claude-plugin/plugin.json`. The packaged configuration field schema is `skills/contract-brand-research/references/config.example.yaml`; do not recreate a root-level configuration template.

Before a change, inspect the current branch and follow the `main` → `develop` → `feature/*` integration workflow and validation commands defined in `AGENTS.md`.
