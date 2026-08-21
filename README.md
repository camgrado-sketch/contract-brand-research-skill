# Contract Brand Research Skill

> A cross-agent workflow for evidence-backed competitor research in contract furniture and B2B design.

This repository packages a single reusable Skill that moves through three controlled stages: **clarify the user's real question**, **research and explain the mechanism with evidence**, and **optionally derive reviewable knowledge-base artifacts**. It is designed first for Manus and Codex, with low-cost Claude Code compatibility.

## 如何调用这个 Skill

### 方式一：显式调用

在 Manus 中，最稳定的方式是在请求开头写出 `$contract-brand-research`：

```text
$contract-brand-research
请分析 Brunner 的商业模式，重点解释它为什么能够以较高价格进入大量公共工程与 Contract 项目。请覆盖品牌定位、产品平台、销售渠道、项目与客户构成，以及其溢价逻辑。
```

该显式调用名也写入了 `skills/contract-brand-research/agents/openai.yaml`。

### 方式二：自然语言调用

当请求明确涉及 Contract 家具竞品研究时，也可以通过自然语言触发，包括品牌定位、产品体系、CMF、定价与溢价逻辑、销售网络、项目案例、客户结构或战略启示等主题：

```text
请研究 Arper 在高端办公公共区域中的品牌定位，包括产品体系、CMF 特征、销售模式和项目客户构成，并分析它对 GRADO 产品研发的启示。在开始搜索前，请先通过几个关键问题确认我的研究意图。
```

### 方式三：指定阶段调用

如果只希望执行前期的意图对齐阶段，可以明确限定范围：

```text
请使用 Contract Brand Research，只执行第一阶段“Intent Alignment（意图对齐）”。我目前有一个关于 2026 年模块化软体沙发研发方向的模糊问题。请一次只问我一个问题，在对齐完成前不要搜索网络、识别图片或直接给出实质性结论。
```

在 Alignment Brief（对齐简报）确认后，再进入证据分析阶段：

```text
研究范围已经确认。请继续使用 $contract-brand-research 进入第二阶段“Evidence-backed Analysis（基于证据的分析）”。优先使用品牌官网、官方图册、年度报告和项目页面，并严格区分 Fact、Analysis 和 Unverified 信息。
```

### 完整调用模板

开始一次完整竞品研究时，可以直接复制并填写以下模板：

```text
$contract-brand-research

研究对象：
研究课题：
核心问题或矛盾：
当前工作假设：
参考框架或对标范围：
地理范围与时间范围：
重点分析维度：
预期交付成果：
是否需要同步至 Obsidian：是 / 否

补充约束：
- 研究开始前一次只提出一个澄清问题。
- 在 Alignment Brief 确认前，不要搜索网络、识别图片或提供实质性结论；除非我明确要求跳过澄清阶段。
- 优先使用官方一手来源，并分别标注 Fact、Analysis 和 Unverified 信息。
```

标准执行顺序是：首先一次只提出一个澄清问题；然后形成包含核心问题、当前假设、参考框架、决策用途、研究范围和重点维度的 Alignment Brief；等待用户确认或明确跳过；确认后再开展基于证据的研究；只有在用户明确要求并批准映射方案后，才进行知识库同步。

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
