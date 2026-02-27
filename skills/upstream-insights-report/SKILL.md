---
name: upstream-insights-report
description: Use when writing deep-dive investment research reports in Traditional Chinese for 上游洞見 (Upstream Insights) style — niche hardware/semiconductor/supply-chain topics targeting Taiwan investors with a 1-3 year horizon. Also use when evaluating whether a topic is niche enough, or when selecting the best research angle from competing candidates.
---

# 上游洞見 Industry Report Skill

## Core Principle

**The research moat IS the report.** A good topic requires reading IEDM papers, commodity specialist reports, and vendor product pages — not Bloomberg summaries. If the information is easy to find, the topic is too mainstream.

## Topic Selection Criteria (1-10 scale each)

| Criterion | Target | Red Flag |
|---|---|---|
| Niche-ness | >8 | Bloomberg/Reuters coverage exists |
| Taiwan supply chain depth | >7 | Only TSMC as generic foundry |
| Timeline realism (1-3 yr) | >8 | <5 = too early or too late |
| Research difficulty | >8 | Info in one Google search |

**Signal**: If 2+ independent agents converge on the same topic unprompted, trust it.

**Good topic anatomy**: Macro trend everyone knows + enabling sub-technology almost nobody writes about + Taiwan supply chain angle + shocking number only derivable by cross-referencing non-obvious sources.

## Non-Obvious Source Types (always check)

- **Conference papers**: IEDM, IITC, VLSI Symposium, SPIE Lithography, APEC
- **Commodity specialists**: SFA Oxford (PGMs), USGS MCS, Johnson Matthey PGM reports
- **Vendor product pages**: Often 12+ months ahead of press coverage
- **Specialist blogs**: BALD Engineering (ALD chemistry), Semiconductor Engineering, Vik's Newsletter
- **Taiwan-specific**: DigiTimes Chinese, 工商時報, 公開資訊觀測站 (MOPS) filings

## Report Structure (上游洞見 Format)

1. **結論** (first) — investment thesis, key stocks with codes, honest role assessment
2. **需求面** — demand logic from first principles, quantified
3. **技術背景** — technology explained from first principles
4. **供給面** — raw materials, constraints, original supply/demand math
5. **供應鏈** — full chain map, Taiwan position honestly assessed
6. **時程路線圖** — catalyst table by node/year
7. **台廠介紹** — each company: 介紹→角色→財務→關注重點; mark "confirmed/probable/unconfirmed"
8. **國際廠商介紹** — same structure, include CEO quotes with attribution
9. **參考來源** — 40+ sources including non-obvious ones

## Chart Placeholders

Every logical chart position gets:
```
【圖表：[description]
[data]
資料來源：[sources]；自行整理】
```

## Quality Gates

- [ ] At least one original calculation not found in financial media
- [ ] Earnings call quotes with attribution (CEO name, quarter, exact words)
- [ ] Taiwan supply chain: "confirmed" / "probable" / "cannot confirm from public data"
- [ ] 40+ min read length (~60–80KB markdown)
- [ ] 40+ references, biased toward non-obvious sources

## PDF Generation (Windows, Chrome headless)

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless=new --disable-gpu --no-sandbox \
  --print-to-pdf="OUTPUT.pdf" --print-to-pdf-no-header \
  "file:///HTML_PATH" 2>/dev/null
```

Use `py` (not `python3`) on this Windows machine. Use `markdown` + `fenced_code` + `tables` extensions.

## Past Reports (Reference)

- `project/HAMR 技術推動 HDD 產業新革命...html` — storage tech supply chain
- `project/兩奈米下的特用化學品...html` — TSMC 2nm specialty chemicals
- `project/川普關稅 2.0 下的供應鏈重構.html` — macro policy supply chain
- `project/光電共封裝CPO產業報告.md` — CPO silicon photonics (written by Claude)
- `project/釕金屬互連產業報告.md` — Ruthenium BEOL interconnects (written by Claude)
