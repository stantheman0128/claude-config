---
name: upstream-insights-report
description: Use when writing deep-dive investment research reports in Traditional Chinese for 上游洞見 (Upstream Insights) style — niche hardware/semiconductor/supply-chain topics targeting Taiwan investors with a 1-3 year horizon. Also use when evaluating whether a topic is niche enough, or when selecting the best research angle from competing candidates.
---

# 上游洞見 Industry Report Skill

## Core Principle

**The research moat IS the report.** A good topic requires reading IEDM papers, commodity specialist reports, and vendor product pages — not Bloomberg summaries. If the information is easy to find, the topic is too mainstream.

## Skill 資料夾結構

本 skill 包含以下資源，請在需要時讀取：

- `gotchas.md` — Claude 撰寫報告時的常見錯誤與修正方法（**開始寫報告前必讀**）
- `references/evaluation-criteria.md` — 選題評分標準與好題目特徵
- `references/source-types.md` — 非顯而易見來源的完整清單
- `templates/report-template.md` — 報告骨架模板（可複製使用）
- `templates/pdf-generation.md` — Markdown → PDF 的完整流程
- `scripts/html_extractor.py` — 從 HTML 參考報告提取純文字的工具

## Topic Selection Quick Check

| Criterion | Target | Red Flag |
|---|---|---|
| Niche-ness | >8 | Bloomberg/Reuters coverage exists |
| Taiwan supply chain depth | >7 | Only TSMC as generic foundry |
| Timeline realism (1-3 yr) | >8 | <5 = too early or too late |
| Research difficulty | >8 | Info in one Google search |

詳細評估標準見 `references/evaluation-criteria.md`。

## Report Structure（快速參考）

1. **結論** — 投資論點前置，核心受益公司（含股票代號）
2. **需求面** — 從第一原理推導需求
3. **技術背景** — 從第一原理解釋技術
4. **供給面** — 原材料、供給限制、原創供需計算
5. **供應鏈** — 完整鏈條地圖，誠實標註台灣位置
6. **時程路線圖** — 催化劑表格
7. **台廠介紹** — 每家：介紹→角色→財務→關注重點；標註 confirmed/probable/unconfirmed
8. **國際廠商介紹** — 同結構，含法說會引言
9. **參考來源** — 40+ 來源，偏向非顯而易見來源

完整模板見 `templates/report-template.md`。

## Quality Gates

- [ ] 至少一個原創計算（金融媒體找不到的）
- [ ] 法說會引言含歸屬（CEO 姓名、季度、原文）
- [ ] 台灣供應鏈角色誠實標註（confirmed / probable / unconfirmed）
- [ ] 40+ 分鐘閱讀長度（~60-80KB markdown）
- [ ] 40+ 參考來源，偏向非顯而易見來源
- [ ] 圖表佔位符放在所有邏輯位置

## Chart Placeholder Format

```
【圖表：[description]
[data]
資料來源：[sources]；自行整理】
```

## PDF Generation

見 `templates/pdf-generation.md`。使用 `py`（非 `python3`）。

## 執行歷史（Memory）

每次完成報告後，將以下資訊追加到 `~/.claude/skill-data/upstream-insights-report/history.json` 的 `reports` 陣列：

```json
{
  "topic": "報告主題",
  "date": "YYYY-MM-DD",
  "file_path": "報告檔案路徑",
  "topic_scores": { "niche": 8, "taiwan_depth": 7, "timeline": 9, "research_difficulty": 8 },
  "companies_covered": ["光洋科（1785）", "..."],
  "word_count": 65000,
  "reference_count": 45,
  "notes": "任何值得記錄的觀察"
}
```

**開始新報告前**，先讀取 history.json：
- 檢查是否有重複或過度相似的主題
- 回顧過去的 notes，避免重複犯錯
- 參考過去報告的品質指標作為基準線

## Past Reports（Reference）

- `project/HAMR 技術推動 HDD 產業新革命...html` — storage tech supply chain
- `project/兩奈米下的特用化學品...html` — TSMC 2nm specialty chemicals
- `project/川普關稅 2.0 下的供應鏈重構.html` — macro policy supply chain
- `project/光電共封裝CPO產業報告.md` — CPO silicon photonics
- `project/釕金屬互連產業報告.md` — Ruthenium BEOL interconnects
