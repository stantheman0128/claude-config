---
name: memory-systems
description: Use when the user asks to "implement agent memory", "persist state across sessions", "remember user preferences across conversations", "build long-term memory for a chatbot", or needs cross-session knowledge retention for an AI agent.
---

# Memory Systems Skill

## Core Insight

**Tool complexity matters less than reliable retrieval.** Filesystem agents scored 74% on LoCoMo benchmarks, beating specialized memory tools at 68.5%. Start simple.

## Memory Layers

| Layer | Persistence | When to Use |
|-------|------------|-------------|
| **Working** | Context window only | Always — current conversation |
| **Short-term** | Session-scoped | Intermediate results, conversation state |
| **Long-term** | Cross-session | User preferences, entity registry |
| **Temporal KG** | Cross-session + history | Facts that change over time |

## Framework Selection

| Framework | Best For | Trade-off |
|-----------|---------|-----------|
| **File-system** | Prototyping, simple agents | No semantic search |
| **Mem0** | Multi-tenant, broad integrations | Less specialized |
| **Zep/Graphiti** | Temporal reasoning, enterprise | Advanced features cloud-locked |
| **Letta** | Full agent introspection | Complexity overhead |
| **Cognee** | Multi-hop reasoning, rich graphs | Heavy ingest processing |

## Decision Path

1. **Prototype**: JSON files with timestamps → validate behavior first
2. **Need semantic search**: Mem0 or vector store with metadata
3. **Need relationship traversal / temporal validity**: Zep/Graphiti
4. **Need agent self-management**: Letta or Cognee

## Simple File-System Memory Pattern

```python
import json
from pathlib import Path
from datetime import datetime

MEMORY_FILE = Path("memory/user_prefs.json")

def remember(user_id: str, fact: str):
    data = json.loads(MEMORY_FILE.read_text()) if MEMORY_FILE.exists() else {}
    data.setdefault(user_id, []).append({
        "fact": fact,
        "timestamp": datetime.utcnow().isoformat()
    })
    MEMORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def recall(user_id: str) -> list:
    if not MEMORY_FILE.exists():
        return []
    data = json.loads(MEMORY_FILE.read_text())
    return data.get(user_id, [])
```

## Mem0 Quick Start (when you outgrow files)

```python
from mem0 import Memory

m = Memory()
m.add("User prefers traditional Chinese responses", user_id="user_123")
m.add("User previously ordered classic tiramisu", user_id="user_123")

# Retrieves relevant memories for context injection
results = m.search("What does this user like?", user_id="user_123")
```

## Anti-Patterns

- Stuffing all memories into every context (expensive, degrades performance)
- No temporal validity tracking (stale facts poison responses)
- Over-engineering before validating basic retrieval works
- No consolidation strategy → unbounded memory growth

## For LINE Chatbot Use Case

Use file-system memory to start:
- Per-user JSON file keyed by LINE `userId`
- Store: past orders, stated preferences, opt-in notes
- Inject only top-3 most relevant memories at conversation start
- Upgrade to Mem0 when you hit semantic search needs
