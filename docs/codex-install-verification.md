# Codex Installation and Verification

## What this repository can verify

The repository CI verifies the plugin manifest, shared Skill package, local-resource references, metadata consistency, script syntax, and WikiLink audit behavior. These checks do **not** install the plugin into Codex or prove model routing in a live Codex session.

## What requires a Codex environment

Install the repository through a current, supported Codex or ChatGPT Plugin workflow, such as a local Marketplace source or another supported plugin upload path. The presence of `.codex-plugin/plugin.json` in a clone is not an installation event. Consult the current OpenAI documentation for any IDE-specific support before testing.

## Manual acceptance checklist

Run these checks in a **new Codex session** after installation. Record the actual response and any failure in the review PR.

| Test | Prompt | Expected behavior | Status |
|---|---|---|---|
| Package visibility | Inspect installed plugin or skill list | `contract-brand-research` is visible | Pending Codex environment |
| Explicit invocation | `$contract-brand-research Analyze why a contract furniture brand can maintain premium pricing at scale.` | The first reply asks one clarifying question; it does not browse or answer substantively | Pending Codex environment |
| Natural-language trigger | `I need to understand a contract furniture competitor's positioning, product system, and premium logic.` | The Skill is selected or its Phase 1 behavior is observed | Pending Codex environment |
| Non-trigger guard | `What are the common characteristics of aniline leather?` | The agent gives a normal material answer and does not force the full competitor-research workflow | Pending Codex environment |
| Packaged resource access | After Phase 1 confirmation, request an evidence-led research note | The agent can load `references/`, `templates/`, and `scripts/` inside the installed Skill package | Pending Codex environment |
| Optional private config | Set `SKILL_CONFIG_PATH` to an explicit private file, then request self-brand mapping | The private configuration is used only when provided; base research still works without it | Pending Codex environment |

## Expected resource layout

For standalone installation, preserve this entire directory without flattening it:

```text
contract-brand-research/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── templates/
└── scripts/
```

Do not copy only `SKILL.md`. The Skill deliberately resolves its bundled field schema from `references/config.example.yaml` so the package does not depend on a repository-root configuration file.

## Reporting rule

Use the following status language accurately:

| State | Allowed wording |
|---|---|
| CI and local deterministic checks pass | “Package structure and deterministic validation passed.” |
| Manual Codex checks have not run | “Actual Codex installation and trigger behavior remain pending.” |
| Manual checks succeed in a live Codex environment | “Installed and tested in [environment/version/date].” |

Do not state or imply that a plugin is installed merely because this repository has a valid manifest.
