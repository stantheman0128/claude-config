---
name: report-verifier
description: Use when verifying an investment research report's quality — checking data citations, logical chains, conclusion support, formatting consistency, and factual accuracy. Triggers on "verify report", "驗證報告", "check report quality", "報告品質檢查", or after completing a report draft. Also useful as a final gate before publishing.
---

# 報告品質驗證（Report Verifier）

系統化驗證上游洞見風格產業報告的品質，確保每個主張都有支撐、每個數字都有來源。

## Input

$ARGUMENTS
- 必填：報告 .md 檔案路徑
- 選填：`--strict` 啟用嚴格模式（所有 check 都必須通過）
- 選填：`--fix` 驗證後自動修正可修正的問題

---

## Step 1: 結構完整性檢查

逐一確認報告包含以下章節（缺少任一為 FAIL）：

- [ ] 結論（且位於報告最前面）
- [ ] 需求面
- [ ] 技術背景
- [ ] 供給面
- [ ] 供應鏈
- [ ] 時程路線圖
- [ ] 台廠介紹
- [ ] 國際廠商介紹
- [ ] 參考來源

---

## Step 2: 數據引用驗證

掃描報告中所有數字聲明（市場規模、成長率、價格、產能等），檢查：

| 檢查項目 | PASS 條件 | FAIL 條件 |
|----------|----------|----------|
| 來源標註 | 每個數字旁有來源 | 數字無來源（假精確） |
| 來源品質 | 專業來源（學術、機構） | 全是 Bloomberg/Reuters |
| 來源可查 | URL 或明確出處 | 模糊引用（「根據報導」） |
| 計算可追溯 | 原創計算有推導過程 | 結果沒有推導步驟 |

**程式化斷言**：用 grep 統計「億」「%」「美元」等數字關鍵字出現次數，與有來源標註的次數比對。比率 < 80% 為 WARNING。

---

## Step 3: 邏輯鏈驗證

檢查報告的核心論證鏈：

1. **需求 → 技術**：需求面描述的問題，技術背景是否回答了？
2. **技術 → 供給**：技術需要的材料/設備，供給面是否覆蓋了？
3. **供給 → 供應鏈**：供給面提到的公司，供應鏈地圖是否包含？
4. **供應鏈 → 台廠**：供應鏈中標記台灣的位置，台廠介紹是否對應？
5. **結論 → 全文**：結論提到的每家公司，後文是否有詳細介紹？

每條斷鏈標記為 FAIL 並記錄位置。

---

## Step 4: 台廠角色誠實度檢查

掃描每家台廠的角色描述：

- [ ] 每家公司都有 confirmed / probable / unconfirmed 標註
- [ ] confirmed 有具體佐證（財報、法說會、MOPS 公告）
- [ ] probable 說明了推測依據
- [ ] 沒有把 probable 偷偷寫成 confirmed 語氣

---

## Step 5: 格式與文字品質

| 檢查項目 | 方法 | 閾值 |
|----------|------|------|
| 粗體數量 | grep `**` | > 100 處為 WARNING |
| 翻譯腔 | 搜尋「值得注意的是」「就...而言」「在...方面」 | 任何出現為 WARNING |
| 圖表佔位符 | grep `【圖表` | < 5 個為 WARNING |
| 法說會引言 | 檢查是否有 CEO 姓名 + 季度 | 無歸屬為 FAIL |
| 報告長度 | 字數統計 | < 50KB 為 WARNING |
| 參考來源數 | 計數 | < 40 為 FAIL |
| 繁體中文 | 搜尋簡體字 | 任何出現為 FAIL |

---

## Step 6: 事實抽查（Web Search）

從報告中隨機選取 5 個事實聲明，用 Web Search 交叉驗證：

- 公司市值或營收數字
- 技術節點時程（如「2nm 量產預計 2025」）
- 供應鏈關係聲明（如「X 是 Y 的供應商」）
- 市場規模預測

每個聲明標記：VERIFIED / UNVERIFIABLE / INCORRECT

---

## Step 7: 輸出驗證報告

```markdown
# 報告驗證結果

## 總評
- 狀態：PASS / PASS WITH WARNINGS / FAIL
- 驗證時間：[timestamp]
- 報告：[檔案名]

## 結構完整性：[PASS/FAIL]
[缺少的章節列表]

## 數據引用：[X/Y 有來源] ([比率]%)
[無來源的數字列表，含位置]

## 邏輯鏈：[PASS/FAIL]
[斷鏈列表]

## 台廠角色誠實度：[PASS/FAIL]
[問題列表]

## 格式品質
[各項檢查結果]

## 事實抽查：[X/5 verified]
[每項結果]

## 修正建議（按優先序）
1. [FAIL 項目] — [建議修正]
2. [WARNING 項目] — [建議修正]
```
