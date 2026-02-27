---
name: context-compression
description: Use when the user asks to "compress context", "summarize conversation history", "implement compaction", "reduce token usage", or mentions context compression, long-running agent sessions, or agents that "forget" previous steps.
---

# Context Compression Skill

## Core Insight

Optimize for **tokens-per-task**, not tokens-per-request. Aggressive compression that loses critical info causes re-fetching, which costs more overall.

## Three Production-Ready Approaches

| Method | Compression | Quality | Use When |
|--------|-------------|---------|----------|
| **Anchored Iterative** | 98.6% | Best (3.70) | Long sessions, file tracking matters |
| **Regenerative Summary** | 98.7% | Good (3.44) | Clear phase boundaries, readability needed |
| **Opaque** | 99.3% | Lowest (3.35) | Max savings, re-fetching cheap |

**Anchored Iterative is the default recommendation.** Structure forces preservation.

## Compression Trigger Strategies

| Strategy | Trigger | Trade-off |
|----------|---------|-----------|
| Fixed threshold | 70-80% context utilization | Simple |
| Sliding window | Keep last N turns + summary | Predictable size |
| Task-boundary | At logical task completions | Clean summaries |

## Structured Summary Template

```markdown
## Session Intent
[What the user is trying to accomplish]

## Files Modified
- file.ts: What changed and why

## Decisions Made
- Decision: Rationale

## Current State
- Tests: X passing, Y failing
- Blockers: None

## Next Steps
1. ...
```

## Probe-Based Quality Check

After compression, ask these questions — if the agent can answer correctly, compression preserved what matters:

| Probe | Question |
|-------|---------|
| Recall | "What was the original error message?" |
| Artifact | "Which files have we modified?" |
| Continuation | "What should we do next?" |
| Decision | "What did we decide about X?" |

## Anti-Patterns

- Compressing system prompts (never do this)
- Using tokens-per-request as the metric
- No separate tracking for artifact trail (files modified)
- Compressing too aggressively on first trigger
