---
name: context-optimization
description: Use when the user asks to "optimize context", "reduce token costs", "improve context efficiency", "implement KV-cache optimization", "implement prompt caching", or discusses context limits, observation masking, context budgeting, or extending effective context capacity.
---

# Context Optimization Skill

## Four Primary Optimization Strategies

1. **Compaction** — Summarizing context contents when approaching limits, targeting 50-70% token reduction with minimal quality loss

2. **Observation Masking** — Replacing verbose tool outputs with compact references, achieving 60-80% reduction in masked observations

3. **KV-Cache Optimization** — Reusing cached Key-Value tensors across requests sharing identical prefixes, targeting 70%+ hit rates. For Claude API: use `cache_control: {type: "ephemeral"}` on stable content (system prompts, knowledge bases). Cache TTL is 5 minutes; costs 25% of base write price, reads cost 10%.

4. **Context Partitioning** — Distributing work across isolated sub-agent contexts for separation of concerns

## Key Implementation Insights

"Context quality matters more than quantity." Tool outputs often comprise 80%+ of agent trajectory tokens — observation masking is most impactful after decisions are made.

Compaction priority order: tool outputs → old conversational turns → retrieved documents (protect system prompts from compression).

Cache optimization: position stable elements (system prompts, tool definitions, knowledge bases) **before** dynamic content to maximize prefix reuse.

## Activation Triggers

Apply when:
- Context utilization exceeds 70%
- Response quality degrades with conversation length
- Costs rising due to large, repeated context (e.g. large system prompt sent every turn)

## Prompt Caching Example (Anthropic API)

```python
client.messages.create(
    model="claude-sonnet-4-6",
    system=[
        {
            "type": "text",
            "text": "<large knowledge base here>",
            "cache_control": {"type": "ephemeral"}  # cache this block
        }
    ],
    messages=[{"role": "user", "content": user_message}]
)
```

Cache the static knowledge base once; only the user message changes each turn. Cost drops ~90% on cached tokens after first request.
