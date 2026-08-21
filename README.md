# Contract Brand Research 竞品品牌研究 Skill

> 面向 Contract 家具与 B2B 设计领域的跨 Agent、基于证据的竞品品牌研究工作流。

本仓库提供一个可复用的 Agent Skill，围绕三个受控阶段展开：**澄清用户真正的问题**、**基于证据研究并解释商业机制**，以及**在用户批准后派生可审阅的知识库成果**。该 Skill 主要面向 Manus 与 Codex，同时兼容 Claude Code。

## 如何调用这个 Skill

### 方式一：显式调用

在 Manus 中，最稳定的方式是在请求开头写出 `$contract-brand-research`：

```text
$contract-brand-research
请分析 Brunner 的商业模式，重点解释它为什么能够以较高价格进入大量公共工程与 Contract 项目。请覆盖品牌定位、产品平台、销售渠道、项目与客户构成，以及其溢价逻辑。
```

该显式调用名也写入了 `skills/contract-brand-research/agents/openai.yaml`。

### 方式二：自然语言调用

当请求明确涉及 Contract 家具竞品研究时，也可以通过自然语言触发，包括品牌定位、产品体系、 CMF、定价与溢价逻辑、销售网络、项目案例、客户结构或战略启示等主题：

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

## 为什么需要这个 Skill

普通的竞品报告通常从宽泛的分析框架开始，最后停留在重复品牌宣传语言。本 Skill 从用户的**不确定性、矛盾或决策问题**出发，要求 Agent 用官方证据检验工作假设，并在输出中明确区分 **Fact（事实）**、**Analysis（分析）** 和 **Unverified（未验证信息）**。

该工作流适用于以下类型的问题：

- 为什么一个 Contract 家具品牌能够在保持高溢价的同时实现规模化收入？
- 经销商网络在品牌商业模式中究竟承担什么作用？
- 哪些 CMF 能力、工程能力或项目交付能力构成了品牌的项目价值？
- 哪些能力可以迁移到另一个品牌，哪些能力不能简单复制？

## 工作流

| 阶段 | Agent 的主要工作 | 主要输出 | 强制边界 |
|---|---|---|---|
| 1. 意图对齐 | 一次只提出一个澄清问题，并形成 Alignment Brief | 已确认的研究问题、工作假设、决策用途、范围和重点维度 | 在确认前不得搜索网络、识别图片或提供实质性结论 |
| 2. 基于证据的分析 | 优先使用官方来源，检验工作假设并解释商业机制 | 研究报告、证据清单、有限范围的自有品牌映射 | 必须区分事实、分析和未验证信息 |
| 3. 可选的知识库同步 | 将已批准的研究内容映射为知识卡，进行有限范围的官网事实补充，并创建可审阅 PR | 研究报告、派生知识卡、素材、链接检查结果和可审阅 PR | 未经用户批准，不得修改知识库或创建 PR |

## 仓库结构

```text
.
├── skills/contract-brand-research/       # 共享 Skill 的唯一事实来源
│   ├── SKILL.md                         # 工作流与触发定义
│   ├── references/                       # 阶段规则、分析维度、来源与证据标准
│   ├── templates/                        # 研究报告、证据清单与 PR 模板
│   └── scripts/                          # 确定性的 PDF 提取和链接审计工具
├── .codex-plugin/                        # Codex / ChatGPT Plugin manifest
├── .claude-plugin/                       # Claude Code Plugin manifest
├── AGENTS.md                             # 仓库级 Agent 协作规则
├── CLAUDE.md                             # Claude Code 对 AGENTS.md 的简要指引
├── .env                                  # 非敏感环境变量模板
└── skills/contract-brand-research/references/config.example.yaml
                                          # 可选私有配置的字段结构示例
```

## 安装

### Manus

将 `skills/contract-brand-research/` 作为 Skill 导入或复制到 Manus 的标准 Skill 目录。必须保留 `SKILL.md`，以及与其配套的 `references/`、`templates/` 和 `scripts/` 目录；仅复制 `SKILL.md` 不足以保证完整运行。

安装后建议新建一个会话，并分别测试显式调用与自然语言触发。测试时应确认 Skill 能够先提出澄清问题，而不是在研究范围未确认前直接搜索网络。

### Codex

通过受支持的 Codex 或 ChatGPT Plugin 工作流安装，例如本地 Marketplace 来源或受支持的 Plugin 上传路径。`.codex-plugin/plugin.json` 是 Plugin 的入口 manifest，但仅仅克隆仓库并不代表 Plugin 已完成安装。

如果采用独立 Skill 方式使用，必须保留完整的 `skills/contract-brand-research/` 目录，包括 `SKILL.md`、`references/`、`templates/` 和 `scripts/`。安装完成后，应在新的 Codex 会话中测试显式调用和自然语言竞品研究请求。IDE 支持会持续变化，请以最新的 [Codex Skills 文档](https://developers.openai.com/codex/skills) 为准。

### Claude Code

可以将仓库目录作为本地 Plugin 进行测试，也可以通过 Claude Code Marketplace 安装。`.claude-plugin/plugin.json` 会暴露同一份 `skills/` 目录。

在本地项目开发期间，建议通过符号链接将共享 Skill 暴露到 `.claude/skills/`，而不是复制出第二份内容。具体方式请参考 [Claude Code Skills 文档](https://code.claude.com/docs/en/skills)。

## 配置

基础竞品研究不依赖配置文件。如果需要加入自有品牌视角或知识库集成，请显式提供私有配置路径，或者设置 `SKILL_CONFIG_PATH` 环境变量。`skills/contract-brand-research/references/config.example.yaml` 只是字段结构参考，并不是必需的运行时文件，也不应被复制为仓库根目录下的第二份配置源。

Skill 有意将以下信息放在核心指令之外：

| 配置区域 | 用途 |
|---|---|
| `self_brand` | 自有品牌定位与战略问题，用于可选的自有品牌映射 |
| `benchmark_brands` | 常用对标品牌集合 |
| `research` | 意图对齐规则与官方事实补充的范围限制 |
| `knowledge_sync` | 目标仓库、路径、模板和分支策略 |
| `review` | 用户确认与 Pull Request 要求 |

不得提交凭据、私人客户信息或专有研究资料。仓库中的 `.env` 只是**占位模板**，不是密钥来源。

## 开发流程

`main` 是经过人工审核的发布分支，`develop` 是集成分支。新的行为变更应从最新的 `develop` 创建 `feature/*` 分支，在功能分支上完成修改并创建指向 `develop` 的 Pull Request。集成后的内容须经过人工审核，才能决定是否发布到 `main`。完整规则请参阅 [AGENTS.md](AGENTS.md)。

## 范围与非目标

初始版本采用以指令为核心的设计，不内置 MCP Server、浏览器自动化、专有数据库或自动写入 Obsidian Vault 的能力。这些属于可选集成，必须得到用户明确批准；未来可以在不改变核心研究方法的前提下增加。

## Codex 验证边界

仓库 CI 只负责验证包结构和确定性行为，不代表已经在真实 Codex 环境中完成安装，也不能证明运行时一定会选择该 Skill。安装后，请在新的 Codex 会话中按照 [Codex 安装与验证说明](docs/codex-install-verification.md) 进行测试，并如实记录验证结果。

## 许可证

本项目采用 MIT License，详见 [LICENSE](LICENSE)。
