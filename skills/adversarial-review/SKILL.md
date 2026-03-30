---
name: adversarial-review
description: Use when reviewing or critiquing an industry research report, investment analysis, or technical deep-dive through multi-perspective debate. Triggers on "review report", "adversarial review", "報告審閱", "辯論審閱", "critique this report", or when the user wants a 3-person panel debate on a report's quality. Also use when user says "/adversarial-review".
---

# 報告辯論審閱（Adversarial Review）

三位評審邊看報告邊即時討論，透過自然對話同時找出問題（防守）與碰撞新洞見（進攻）。使用 Agent Teams 讓 Teammates 直接互相 message，實現真正的「你一言我一語」。

## Skill 資料夾結構

- `gotchas.md` — 辯論審閱常見問題與修正方法（**啟動 team 前必讀**）
- `templates/output-template.md` — 整合輸出的結構化模板（Step 5 使用）
- `templates/role-prompts.md` — 三位評審的完整角色 prompt

## Input

$ARGUMENTS
- 必填：報告 .md 檔案路徑（e.g. `報告_v3.md`）
- 選填：`--focus "問題描述"` 指定最想深挖的議題，自動成為 seed question #1
- 選填：`--plan` 審閱後自動進入 Plan Mode 生成修訂計畫

---

## Step 1: 讀取報告

讀取 $ARGUMENTS 指定的報告全文。如果檔案超過 1200 行，分段讀取但確保完整載入。記錄：
- 總行數、章節結構、引用數量
- 報告主題與核心論點
- 提到的公司清單與對應技術領域

---

## Step 2: 設計 Seed Questions

閱讀報告後，設計 3-5 個 **provocative seed questions**。問題品質直接決定討論品質。

### 設計原則

1. **不能用「是/否」回答** — 必須逼出觀點與論述
2. **刻意製造維度衝突** — 讓不同角色的框架互相碰撞
3. **聚焦在報告的「沉默區域」** — 報告沒寫到但隱含的假設與盲區

### 問題類型參考

- **假設挑戰**：「報告假設 [X]，但如果 [反面情境] 呢？」
- **時間軸爭議**：「報告說 [趨勢] 會在 [時間] 發生，你認為實際時間表是？」
- **贏家預測**：「如果趨勢成真，最大受益者真的是報告提到的這些公司嗎？」
- **盲區探測**：「報告完全沒提到 [X]，這是刻意省略還是真的盲區？」
- **反事實**：「如果 [關鍵變數] 翻轉，整個投資邏輯會怎麼變？」

如果 $ARGUMENTS 包含 `--focus`，將使用者指定的疑慮作為 seed question #1。

---

## Step 3: 建立 Agent Team（3 Teammates）

使用 Agent Teams（不是 Subagents）。每個 Teammate 收到：完整報告文字 + 角色人設 + seed questions。用 Opus 模型確保討論品質。

角色 prompt 見 `templates/role-prompts.md`。

三個角色：
- **黑臉**（資深產業分析師）— 質疑一切，找事實錯誤和邏輯問題
- **紅臉**（產業投資人）— 從投資者角度評估實用價值
- **綠臉**（跨界觀察者）— 打破二元對立，提出第三種可能

---

## Step 4: 討論進行

### 討論是自然對話，沒有回合結構

Teammates 直接互相 message，不要設計 Round 1/2/3。

### Lead 介入規則（克制使用）

- **討論停滯**：超過 2 個來回沒有實質推進 → broadcast 追問
- **循環重複**：辯論打轉 → broadcast 結束該議題
- **自然收斂**：三方共識 → broadcast 繼續下一個
- **補充 follow-up**：碰撞出有價值的點 → 加深討論

### 結束條件

- 所有 seed questions 都已被觸及
- 每個議題都達成共識或明確定義了分歧點
- 討論已產出足夠素材（Lead 判斷）

---

## Step 5: Lead 整合輸出

### 5a. 文字快速掃描

- 粗體是否過度使用
- 有無翻譯腔
- 結論是否先行
- 用語是否統一（繁體中文、台灣用語）

### 5b. 結構化輸出

使用 `templates/output-template.md` 的格式輸出。

### 5c. 黑臉事實核查驗證

黑臉提出的事實性指控，用 Web Search 交叉驗證後才納入最終輸出。

---

## Step 6（可選）: 生成修訂計畫

如果 $ARGUMENTS 包含 `--plan`，基於審閱結果進入 Plan Mode 撰寫修訂計畫。

---

## 執行歷史（Memory）

每次完成審閱後，將以下資訊追加到 `~/.claude/skill-data/adversarial-review/history.json` 的 `reviews` 陣列：

```json
{
  "report_topic": "被審閱的報告主題",
  "date": "YYYY-MM-DD",
  "report_file": "報告檔案路徑",
  "fatal_issues": 2,
  "major_issues": 5,
  "insights_generated": 3,
  "stance_changes": 1,
  "top_insight": "最有價值的碰撞洞見（一句話）",
  "recurring_pattern": "是否出現與過去相同的問題模式"
}
```

**開始新審閱前**，先讀取 history.json：
- 檢查同一份報告是否審閱過（避免重複）
- 回顧 `recurring_pattern`，如果過去反覆出現同樣的問題，直接加入 seed questions
- 追蹤 `insights_generated` 和 `stance_changes` 趨勢，評估審閱品質是否在提升

---

## 注意事項

- **必須使用 Agent Teams**（不是 Subagents）
- **討論是自然對話，不是回合制**
- **每次發言限 150 字**
- **Lead 克制介入** — 主要價值在 Step 2 和 Step 5
- **立場變化是寶藏** — 務必記錄
- **所有內容使用繁體中文** — 台灣用語
