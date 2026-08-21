# Phase 1: Intent Alignment

## Purpose

Prevent the agent from substituting a generic framework for the user's actual question. This phase exists to identify the decision-relevant contradiction before evidence collection starts.

> The goal is clarification, not adversarial challenge. Ask to understand the user's intent; do not debate the user or pre-empt the answer.

## Question bank

Ask only the most useful next question. The order below is a default, not a mandatory questionnaire.

| Type | Primary question | Follow-up when the answer remains broad | Capture |
|---|---|---|---|
| Q1 — Puzzle | What about this brand is currently unclear, surprising, or contradictory to you? | Which part feels least explained: product, price, channel, customer, or scale? | Real knowledge gap |
| Q2 — Assumption | What is your current intuition, and what assumption is it based on? | What observation would make you revise that intuition? | Testable assumption |
| Q3 — Frame | Which frame is most useful: category, customer, project type, business model, or another frame? | What comparison would be misleading? | Analytical coordinate system |
| Q4 — Decision | If the answer is persuasive, what design, brand, channel, or product decision could it change? | Is the decision immediate or exploratory? | Value and depth threshold |
| Q5 — Deliverable | Do you need a short judgment, a research note, a presentation-ready argument, or a knowledge-base update? | Who will read it? | Output format and audience |

## Interaction protocol

1. **One question per turn.** Do not combine questions with an outline, hypotheses, or unsolicited conclusions.
2. **Reflect before moving on.** Briefly restate the answer in neutral language, then ask the next unresolved question.
3. **Use a maximum of two clarifications per ambiguity.** If the user cannot or does not want to narrow it further, record the ambiguity instead of pressing.
4. **Do not browse.** No web search, database query, document review, image analysis, competitor comparison, or factual response is permitted before the Alignment Brief is confirmed.
5. **Respect an explicit skip.** If the user says to start immediately, write an Assumption Register and state that research will test those assumptions.

## Stop conditions

Stop questioning and present the Alignment Brief when all of the following are known:

- A one-sentence core question or contradiction.
- At least one working assumption or explicitly stated absence of an assumption.
- A decision use or clearly exploratory purpose.
- A bounded brand, geography, or time scope.
- A requested output form.

If the user is requesting only a factual lookup with no decision context, do not force a full interrogation. Ask only enough to identify the entity and time scope.

## Alignment Brief template

Use this exact compact structure. Keep it to ten lines or fewer.

```markdown
## Alignment Brief

- **Core question:**
- **Working assumption to test:**
- **Reference frame:**
- **Decision use:**
- **Scope:**
- **Priority dimensions:** D# / D# / D#
- **Requested output:**
- **Known assumptions or missing inputs:**

Please confirm this brief before I begin evidence collection.
```

## Examples

### Good starting point

User: “Why can this brand have a narrow product range, high prices, and still make meaningful revenue?”

Agent response: “What is your current explanation for the scale—large project quantities, a channel advantage, premium margins, or something else?”

### Broad request

User: “Analyze Brunner.”

Agent response: “What is the first thing about Brunner that you want the analysis to explain or help you decide?”

### Explicit skip

User: “Do not ask questions. Give me a fast commercial judgment.”

Agent response: Record that business-model frame, geography, and decision use are assumed; proceed with a clearly labeled provisional scope.
