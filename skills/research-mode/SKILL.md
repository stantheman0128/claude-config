---
name: research-mode
description: Use when the user says "/research-mode", "research mode", "研究模式", "唯讀模式", "read-only mode", or when the user wants to explore and analyze code without accidentally modifying anything. Blocks all Edit, Write, and file-writing Bash commands for the rest of the session.
---

# Research Mode（研究模式）

啟用後，PreToolUse hook 會阻擋所有檔案修改操作，只允許讀取和搜尋：

**阻擋的操作：**
- `Edit` / `Write` / `NotebookEdit` 工具
- Bash 中的 `>`, `>>`, `tee`, `mv`, `cp`, `mkdir`, `touch`

**允許的操作：**
- `Read` / `Glob` / `Grep` / `Bash`（純讀取指令）
- `WebFetch` / `WebSearch`
- All MCP tools / Agent / Subagent

## 啟用

```bash
touch ~/.claude/.research-mode
```

啟用後回覆使用者：「Research mode 已啟用。所有檔案修改操作已被阻擋，只允許讀取和搜尋。」

## 關閉

使用者說 "/research-off" 或 "關閉研究模式" 時：

```bash
rm ~/.claude/.research-mode
```

## 使用場景

- 研究不熟悉的 codebase 時，防止意外修改
- Debug 時只想加 log 觀察，不想改其他東西
- 閱讀和分析報告時，防止 Claude 自作主張修改
