# Phase 3: Optional Knowledge Sync

## Purpose

Convert an approved research result into durable, traceable knowledge-base artifacts without turning a focused analysis into uncontrolled second-round research.

Run this phase only after the user explicitly asks to archive, synchronize, update, or derive knowledge cards.

## Preconditions

Before changing any target repository:

1. Inspect its nearest instruction file, contribution rules, note schema, templates, index pages, attachment conventions, and current git state.
2. Identify the target repository, branch policy, and whether a pull request is required.
3. Present a proposed mapping of source notes, derived cards, visual assets, and paths.
4. Obtain explicit approval for that mapping.

## Classify artifacts

| Artifact type | Purpose | Typical location | Required label |
|---|---|---|---|
| Research note | Full argument, source ledger, caveats, calculations | Research or reference area | `source_type: research-synthesis` |
| Derived knowledge card | Fast retrieval and reuse of stable findings | Formal knowledge area | `source_type: derived-card` |
| Evidence card | Key data, sources, cases, and confidence | Formal knowledge area | `source_type: evidence-index` |
| Derived visual | Explains a mechanism or calculation | Adjacent to research note | Caption: `derived visualization` |
| External source | Official report, page, or catalogue | Keep external; store link only | Source grade and access date |

Do not call a research synthesis an external primary source. Preserve the external primary-source links inside it.

## Template mapping

Map analysis content to existing user templates. Do not create a new taxonomy simply because a field is missing.

### General Mapping

| Analysis content | Likely output | Mapping rule |
|---|---|---|
| Positioning, product system, applications, strengths, boundaries | Brand positioning card | This is the main navigation entry. |
| Short, medium, and full verbal descriptions | Brand expression card | Distinguish official language from research wording. |
| Scale facts, channels, project evidence, source links | Evidence or brand asset card | Preserve source grade and reporting period. |
| Full reasoning, source ledger, calculations, caveats | Research note | Link to every derived card. |

### Obsidian DBS Mode Mapping (V2.0)

| Analysis content | DBS Template | Target Path (M1-Foundation) |
|---|---|---|
| Full reasoning, source ledger, caveats | `设计师研究底稿` | `Product-Technical/Research-Notes/` |
| Positioning, market level, gaps | `品牌定位卡` | `Brand-Expression/` |
| Multi-length verbal descriptions | `品牌表达模块卡` | `Brand-Expression/` |
| Assets, permissions, source links | `品牌证据与资产卡` | `Brand-Expression/` |
| Product series & technical facts | `产品｜01 系列主卡` | `Product-Technical/` |

**DBS Metadata Requirements:**
- MUST include `domain: design-business-support` and `module: foundation`.
- MUST set `evidence_status: to-validate`.
- MUST follow the `research_candidate_*` routing protocol for new or substantively updated notes.

## Official top-up pass

Research notes often answer a specific question rather than every card field. Before generating cards, run a bounded gap review:

1. Compare each template field against the research note.
2. Mark every field as **Covered**, **Officially fillable**, or **Unverified**.
3. For Officially fillable fields, consult official reports, official website pages, official catalogues, or regional official sites only.
4. Use no more than five pages or documents by default.
5. Mark unresolved fields `Unverified` or `To verify`; do not invent text to eliminate blank fields.

This pass must not use trade media and must not expand into a second research project.

## Card-writing rules

- Use the repository's existing frontmatter and status vocabulary.
- Separate **Official self-description**, **Research analysis**, and **Unverified** statements inside each card.
- Use stable filename links, not fragile path-specific wiki links, unless repository rules require otherwise.
- Put images and charts in repository-relative locations. Never leave local absolute file paths.
- Link main card → expression card, evidence card, and research note; link every research note → all derived cards.
- Add only a minimal entry to an existing index or MOC. Do not add an index hierarchy without approval.

### Obsidian DBS Specific Rules

1.  **Source List Strategy**:
    - `source` MUST be a YAML list if more than one source exists.
    - Each `[[Internal Note]]` or external URL MUST be a separate list item.
    - NEVER mix WikiLinks and descriptive text in a single scalar `source` value.
2.  **Tag Suggestions**:
    - SUGGEST tags ONLY from controlled namespaces: `mkt/`, `brand/`, `cmf/`, `space/`, `biz/`.
    - Set `tag_review_status` ONLY to `pending` or `needs-review`. NEVER set to `approved`.
3.  **In-body Evidence Links**:
    - Use the format `[Name](URL) [n]` for the first occurrence of an official case, project, or showroom in the body.
    - Ensure `[n]` corresponds to the same URL in the References/Evidence section.

## Pull-request discipline

1. Start from the latest integration branch specified by the target repository.
2. Create a narrow topic branch; never commit directly to a protected release branch.
3. Validate changed-file scope, YAML, Markdown, wiki links, and asset references before commit.
4. Write the PR body into a Markdown file first, then submit that file as the PR body. This prevents escaped newline artifacts.
5. PR body must contain: overview, change table, source and derived-status note, validation checklist, and review focus.
6. Open the PR page or retrieve the rendered body to confirm readable Markdown after submission.
7. If the base branch changes and conflicts occur, rebuild from the latest base branch instead of force-pushing an old history.

## Completion checklist

- [ ] User approved source-versus-derived paths and mapping.
- [ ] Gaps were identified before the official top-up pass.
- [ ] Official top-up stayed within allowed sources and page limit.
- [ ] Every new card links to its supporting research note.
- [ ] All external claims retain source and confidence information.
- [ ] Validation is clean and PR body renders as Markdown.
