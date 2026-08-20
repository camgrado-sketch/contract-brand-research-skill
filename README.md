# Contract Brand Research Skill

> A cross-agent workflow for evidence-backed competitor research in contract furniture and B2B design.

This repository packages a single reusable Skill that moves through three controlled stages: **clarify the user's real question**, **research and explain the mechanism with evidence**, and **optionally derive reviewable knowledge-base artifacts**. It is designed first for Manus and Codex, with low-cost Claude Code compatibility.

## Why this Skill exists

Generic competitor reports usually start from a broad framework and end by repeating brand marketing language. This Skill starts instead from a user's uncertainty, contradiction, or decision. It requires the agent to test assumptions against official evidence and to visibly distinguish **Fact**, **Analysis**, and **Unverified** statements.

The workflow was designed for questions such as: *Why can a contract furniture brand maintain premium pricing at scale?*; *What is the real role of its dealer network?*; *Which CMF or operating capabilities create its project value?*; and *Which capabilities are transferable to another brand?*

## Workflow

| Stage | What the agent does | Output | Hard boundary |
|---|---|---|---|
| 1. Intent alignment | Asks one clarifying question at a time and writes an Alignment Brief | Confirmed research question, assumptions, decision use, scope, priority dimensions | No web search, image inspection, or substantive answer |
| 2. Evidence-backed analysis | Uses official sources first, tests assumptions, and explains a commercial mechanism | Research note, evidence ledger, bounded self-brand mapping | Facts, analysis, and unverified claims stay separate |
| 3. Optional knowledge sync | Maps approved research to knowledge cards, performs a bounded official top-up, then creates a PR | Research note, derived cards, assets, link checks, reviewable PR | No repository modification without user approval |

## Repository structure

```text
.
├── skills/contract-brand-research/  # Shared Skill source of truth
│   ├── SKILL.md                     # Workflow and trigger definition
│   ├── references/                  # Phase rules, dimensions, source and evidence standards
│   ├── templates/                   # Research, evidence, and PR templates
│   └── scripts/                     # Deterministic PDF extraction and link audit helpers
├── .codex-plugin/                   # Codex / ChatGPT plugin manifest
├── .claude-plugin/                  # Claude Code plugin manifest
├── AGENTS.md                        # Repository-wide agent collaboration rules
├── CLAUDE.md                        # Thin Claude Code pointer to AGENTS.md
├── config.example.yaml              # Private-context configuration schema
└── .env                             # Non-secret environment variable template
```

## Installation

### Manus

Import or copy `skills/contract-brand-research/` as a Skill. Keep `SKILL.md` together with its `references/`, `templates/`, and `scripts/` directories.

### Codex

Use the repository as a Skill-only Plugin. Codex recognizes the manifest at `.codex-plugin/plugin.json`, which points to `./skills/`. For repo-scoped development, expose the shared Skill under `.agents/skills/` with a symlink rather than creating a second copy. See the [Codex Skills documentation](https://developers.openai.com/codex/skills).

### Claude Code

Test with the repository directory as a local plugin, or install it through a Claude Code marketplace. The manifest at `.claude-plugin/plugin.json` exposes the same `skills/` directory. For local project development, expose the shared Skill under `.claude/skills/` with a symlink rather than creating a second copy. See the [Claude Code Skills documentation](https://code.claude.com/docs/en/skills).

## Configuration

Copy `config.example.yaml` to an untracked local `config.yaml` when you need a self-brand lens or knowledge-base integration. The Skill intentionally keeps these values outside its core instructions:

| Configuration area | Purpose |
|---|---|
| `self_brand` | Brand positioning and strategic questions for optional self-brand mapping |
| `benchmark_brands` | Common comparison set |
| `research` | Alignment and official top-up limits |
| `knowledge_sync` | Target repository, paths, templates, and branch policy |
| `review` | User-confirmation and pull-request requirements |

Never commit credentials, private client data, or proprietary research. The committed `.env` file is a **placeholder-only template**, not a source of secrets.

## Development workflow

`main` is the human-reviewed release branch. `develop` is the integration branch. Build behavior changes on `feature/*` branches from the latest `develop`, open a PR into `develop`, and obtain human approval before release decisions. Full rules are in [AGENTS.md](AGENTS.md).

## Scope and non-goals

The initial release is intentionally instruction-first. It does not bundle an MCP server, browser automation, a proprietary database, or automatic writing to an Obsidian vault. These are optional integrations that require explicit user approval and may be added later without changing the core research method.

## License

MIT. See [LICENSE](LICENSE).
