---
name: model-effort-router
description: Use when 需要決定一個任務該用哪個 Claude 模型與哪個 effort 檔位，或被問「用哪個模型」「opus 還是 sonnet 還是 fable」「effort 設多少」「subagent 用什麼檔」「ultracode 是什麼」「這樣跑會不會太貴」時。也用於審視既有的模型/effort 選擇是否踩雷（安全稽核用錯模型、對話中途換檔、max 濫用）。純分類與建議，不執行任務本身。
---

# Model / Effort Router

## Overview

任務分類器：輸入任務描述，輸出「模型 + effort + 一行理由 + 雷點」。資料來源為 2026-08 官方 docs 與三份 system card 調研，逐條有據。

## 分類流程

1. 對照下方決策表選出模型與 effort 起點。
2. 逐條檢查硬規則，命中就修正。
3. 按輸出格式回答，不展開長篇。

## 決策表

| 任務類型 | 模型 @ effort | 依據 |
|---|---|---|
| 日常編修、問答、單檔小改 | Sonnet 5 @ high | 逼近 Opus 4.8 級、最便宜；要再省用 medium（≈ Sonnet 4.6 high） |
| 批次量產、subagent 派工 | 同 session 模型 @ low~medium | 官方點名 low 適合 subagent；低檔會合併 tool call、直接動手 |
| 難 coding、多檔重構、agentic 長活 | Opus 5 @ xhigh | 官方建議起點；SWE-bench Verified 96.0%、FrontierBench 44.4%（xhigh 為峰值） |
| 安全稽核、漏洞挖掘 | Opus 5 @ xhigh | Opus 5 明文允許原始碼層級漏洞挖掘；**絕不用 Fable**（見硬規則 1） |
| 電腦操作、vision、文件/簡報知識工作 | Opus 5 @ high~xhigh | OSWorld 2.0 70.6、GDPval-AA Elo 1861 皆三者最高 |
| 最深推理、研究級數學、小時級超長程 | Fable 5 @ high 起跳 | ARC-AGI-1 98.5%、RiemannBench 55%、FrontierSWE #1；官方：Fable 低檔常勝前代 xhigh，不必預設開高 |
| 大規模平行（稽核全 repo、遷移、多視角驗證） | ultracode 或明講「用 workflow」 | 這是編排方式不是檔位；引擎上限 16 併發 / 1000 agent |

## Effort 速查

- 五檔：`low` / `medium` / `high`（預設，＝不帶參數）/ `xhigh` / `max`。沒有「extrahigh」。
- 是行為訊號不是硬預算，影響所有 token（thinking、tool call 數、前後言）。
- `xhigh` 只在 Fable 5 / Mythos 5 / Opus 5 / Opus 4.8 / 4.7 / Sonnet 5；Opus 4.6 / Sonnet 4.6 只有 low/medium/high/max。
- 實測曲線：Opus 5 FrontierBench low 25%（省 64% token）→ high 39% → xhigh 44.4% → **max 43%（不再漲）**；Fable 5 ARC-AGI-1 low 90.5%/$1.45 → max 98.5%/$5.45 每題。官方唯一倍率：高檔 vs 低檔約 7x token。
- 官方立場：「調 effort 常比換模型更好的槓桿」；effort 刻度逐模型校準，同名檔位跨模型不等值。

## 模型特性速查

| | Sonnet 5（$3/$15） | Opus 5（$5/$25） | Fable 5（$10/$50） |
|---|---|---|---|
| 定位 | 量產工作馬，不推前沿 | 性價比王，cutoff 2026-05 最新 | Mythos-class，深推理與超長程 |
| thinking | adaptive 預設開；嚴格照 effort 辦事，low 會刻意少做 | 預設開；`disabled` 只能配 ≤high；effort 不縮短可見輸出 | 永遠開、關不掉；raw CoT 永不回傳；單請求可跑數十分鐘 |
| prompt 脾氣 | 指令字面化服從，舊加重語氣會過度觸發 | 自帶自我驗證（刪 double-check 鷹架）；愛派 subagent 要設上限 | 過度指令化反而降質，要 de-prescribe |

## 硬規則（逐條檢查）

1. **安全/攻防/漏洞任務不用 Fable 5**：cyber 分類器整段擋（FrontierBench 實測 42% API call 被擋、26% trial fallback 成 Opus 4.8），改 Opus 5。
2. **一段對話固定一檔**：改 effort 會改 rendered prompt，prompt cache 全滅重寫。
3. **max 先測再用**：官方警告易 overthink、貴；Opus 5 實測 max 不比 xhigh 高分。預設答案給 xhigh，max 只在「正確性遠比成本重要且已測過」才給。
4. **ultracode 不是 effort 檔位**：是 Claude Code 設定＝送 xhigh + 自動 workflow 編排，session-only；settings 的 `effortLevel` 不收 max/ultracode；`CLAUDE_CODE_EFFORT_LEVEL` 蓋過一切且非 xhigh 時 ultracode 失效。
5. **xhigh/max 要配大 max_tokens**（API 起點 64k），否則 thinking 吃掉預算、回答被截斷。
6. Sonnet 5 新 tokenizer 同文字 +30% token：從 4.6 搬來的 max_tokens/成本估算要重算。

## 輸出格式

```
模型：<X>（備援：<Y>）
Effort：<檔位>
理由：<一行，引用上表依據>
雷點：<命中的硬規則，無則省略>
```

## 常見錯誤

| 錯誤 | 正解 |
|---|---|
| 「最強任務→Fable」反射 | Opus 5 晚發六週，多數 agentic/coding 頭對頭追平或反超，半價；Fable 留給深推理/超長程 |
| 把 ultracode 當第六檔 | 它是編排設定；最深推理設 max（先測） |
| 安全稽核選 Fable「因為最聰明」 | 硬規則 1，會被自家分類器擋 |
| 對話中途降檔省錢 | cache 重寫反而更貴 |

## 資料時效

2026-08-06 調研。Sonnet 5 優惠價 $2/$10 至 2026-08-31 止。新模型發佈或大版本更新後，先查 platform.claude.com/docs 的 models overview 與 effort 頁再回答，數字過期就別引用。
