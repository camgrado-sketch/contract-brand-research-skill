# Contract Brand Research Skill

> A cross-agent workflow for evidence-backed competitor research in contract furniture and B2B design.

This repository packages a single reusable Skill that moves through three controlled stages: **clarify the user's real question**, **research and explain the mechanism with evidence**, and **optionally derive reviewable knowledge-base artifacts**. It is designed first for Manus and Codex, with low-cost Claude Code compatibility.

## How to call the Skill

### Explicit invocation

For the most reliable invocation in Manus, place `$contract-brand-research` at the beginning of the request:

```text
$contract-brand-research
Please analyze Brunner's business model, focusing on why it can sustain premium pricing while entering a large volume of public-sector and contract projects. Cover brand positioning, product platform, sales channels, project and customer composition, and premium logic.
```

The explicit invocation name is also declared in `skills/contract-brand-research/agents/openai.yaml`.

### Natural-language invocation

The Skill can also be triggered by a request that clearly concerns contract-furniture competitor research, including brand positioning, product systems, CMF, pricing or premium logic, sales networks, project cases, customer structure, or strategic implications:

```text
Please research Arper's positioning in high-end office public areas, including its product system, CMF characteristics, sales model, and project customers. Explain the implications for GRADO's product development. Before searching, ask a few key questions to confirm my research intent.
```

### Phase-specific invocation

To run only the intent-alignment stage, state the boundary explicitly:

```text
Use Contract Brand Research and execute only Phase 1: Intent Alignment. I have a vague question about the 2026 development direction for modular upholstered sofas. Ask one question at a time, and do not search the web, inspect images, or provide a substantive conclusion.
```

After the Alignment Brief has been confirmed, continue with evidence-backed analysis:

```text
The research scope is confirmed. Continue with $contract-brand-research Phase 2: Evidence-backed Analysis. Prioritize official websites, catalogues, annual reports, and project pages. Clearly separate Fact, Analysis, and Unverified claims.
```

### Complete request template

Use the following template when starting a full research task:

```text
$contract-brand-research

Research subject:
Research topic:
Core question or contradiction:
Current working assumption:
Reference frame or comparison scope:
Geography and time period:
Priority dimensions:
Expected deliverable:
Need Obsidian knowledge sync: Yes / No

Additional constraints:
- Ask one clarification question at a time before researching.
- Do not search, inspect images, or provide a substantive answer until the Alignment Brief is confirmed, unless I explicitly ask you to skip clarification.
- Prioritize official primary sources and label Fact, Analysis, and Unverified information separately.
```

The expected sequence is: ask one clarification question at a time; prepare an Alignment Brief covering the core question, assumption, reference frame, decision use, scope, and priority dimensions; wait for confirmation or an explicit skip; then conduct evidence-backed research; and only perform knowledge-base synchronization after the user explicitly requests and approves the mapping.

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
├── .env                             # Non-secret environment variable template
└── skills/contract-brand-research/references/config.example.yaml
                                      # Packaged field schema for optional private configuration
```

## Installation

### Manus

Import or copy `skills/contract-brand-research/` as a Skill. Keep `SKILL.md` together with its `references/`, `templates/`, and `scripts/` directories.

### Codex

Install through a supported Codex or ChatGPT Plugin workflow, such as a local Marketplace source or a supported plugin upload path. The manifest at `.codex-plugin/plugin.json` is the package entry point, but its presence in a cloned repository does **not** mean the plugin is installed. For standalone use, preserve the complete `skills/contract-brand-research/` directory, including `SKILL.md`, `references/`, `templates/`, and `scripts/`; copying `SKILL.md` alone is insufficient. After installation, start a new session and test both an explicit invocation and a natural-language competitor-research request. IDE support changes over time and should be checked against the current [Codex Skills documentation](https://developers.openai.com/codex/skills).

### Claude Code

Test with the repository directory as a local plugin, or install it through a Claude Code marketplace. The manifest at `.claude-plugin/plugin.json` exposes the same `skills/` directory. For local project development, expose the shared Skill under `.claude/skills/` with a symlink rather than creating a second copy. See the [Claude Code Skills documentation](https://code.claude.com/docs/en/skills).

## Configuration

Base research works without configuration. When you need a self-brand lens or knowledge-base integration, provide a private configuration path explicitly or set `SKILL_CONFIG_PATH` to that path. The packaged schema at `skills/contract-brand-research/references/config.example.yaml` is a field reference only; it is not a required runtime file and should not be copied as a second source of truth at the repository root. The Skill intentionally keeps these values outside its core instructions:

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

## Codex verification boundary

Repository CI verifies package structure and deterministic behavior. It does not install the package into a live Codex environment or prove runtime trigger selection. Follow [Codex Installation and Verification](docs/codex-install-verification.md) in a new Codex session after installation, and record the outcome accurately.

## License

MIT. See [LICENSE](LICENSE).
