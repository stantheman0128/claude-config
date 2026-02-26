# Claude Code 個人設定

我的 Claude Code 編輯器配置、自訂代理人與工作流程指南，用於在多台電腦間同步設定。

## 📁 檔案說明

### 核心設定檔

- **settings.json** — Claude Code 的全域配置檔案
  - 已啟用的插件清單（frontend-design、context7、code-review、github 等）
  - 權限規則：允許、詢問、拒絕的指令清單
  - 模型預設值與自動更新頻道設定

- **CLAUDE.md** — 工作流程指引與專案管理規範
  - 計劃模式與子代理策略
  - 自我改進循環（lessons.md）
  - 核心原則：簡單優先、無懶惰、最小影響

### agents/ — 自訂專業代理人

放置在 `~/.claude/agents/` 目錄，讓 Claude 可以呼叫這些專屬子代理人：

| 檔案 | 說明 |
|------|------|
| `backend-architect.md` | 後端架構設計專家 |
| `frontend-architect.md` | 前端架構設計專家 |
| `system-architect.md` | 系統整體架構規劃 |
| `security-engineer.md` | 資安檢查與建議 |
| `performance-engineer.md` | 效能分析與優化 |
| `refactoring-expert.md` | 程式碼重構指導 |
| `requirements-analyst.md` | 需求分析與釐清 |
| `tech-stack-researcher.md` | 技術選型研究 |
| `technical-writer.md` | 技術文件撰寫 |
| `deep-research-agent.md` | 深度研究與資料蒐集 |
| `learning-guide.md` | 學習路徑與教學引導 |

### commands/ — 自訂斜線指令

放置在 `~/.claude/commands/` 目錄，作為可重用的提示範本：

| 檔案 / 目錄 | 說明 |
|------------|------|
| `new-task.md` | 建立新任務的標準流程 |
| `industry-report.md` | 產業報告生成指令 |
| `reels.md` | 短影音腳本生成指令 |
| `api/` | API 相關指令集 |
| `supabase/` | Supabase 資料庫操作指令 |
| `ui/` | UI 元件生成指令 |
| `misc/` | 其他雜項指令 |

## 🚀 安裝方法

將整個倉庫內容複製到 Claude Code 設定目錄：

**Linux / macOS**
```bash
cp settings.json ~/.claude/settings.json
cp CLAUDE.md ~/.claude/CLAUDE.md
cp -r agents ~/.claude/agents
cp -r commands ~/.claude/commands
```

**Windows**
```powershell
copy settings.json $env:USERPROFILE\.claude\settings.json
copy CLAUDE.md $env:USERPROFILE\.claude\CLAUDE.md
xcopy agents $env:USERPROFILE\.claude\agents /E /I
xcopy commands $env:USERPROFILE\.claude\commands /E /I
```

## 🔄 多裝置同步

在任何一台電腦上更新設定後，提交並推送到這個倉庫，其他電腦就可以拉取最新配置：

```bash
git add .
git commit -m "更新設定"
git push
```

其他裝置執行：

```bash
git pull
```

然後重新將檔案複製到 `~/.claude/` 目錄即可。
