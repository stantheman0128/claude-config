# 報告辯論審閱（Adversarial Review）

此 command 已升級為完整 skill。執行時請參照 `~/.claude/skills/adversarial-review/SKILL.md` 的完整流程。

核心資源位於 skill 資料夾：
- `gotchas.md` — 開始前必讀
- `templates/role-prompts.md` — 三位評審的角色 prompt
- `templates/output-template.md` — 整合輸出格式

## Input

$ARGUMENTS
- 必填：報告 .md 檔案路徑
- 選填：`--focus "問題描述"`
- 選填：`--plan` 審閱後生成修訂計畫
