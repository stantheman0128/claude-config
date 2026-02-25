# 上游洞見風格產業研究報告生成工作流

Generate a deep, niche industry research report in Traditional Chinese that matches 上游洞見 (Upstream Insights) editorial quality.

## Input

Optional argument: $ARGUMENTS
- If provided: a topic hint, a folder path containing sample reports, or both (e.g. "project/" or "ruthenium semiconductors")
- If empty: autonomously locate sample reports and pick the topic

---

## Step 1: Find and Parse Sample Reports

Look for sample HTML/PDF reports in the current project folder or the path from $ARGUMENTS.
Convert HTML to readable text using Python:

```python
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','head'): self.skip = True
    def handle_endtag(self, tag):
        if tag in ('script','style','head'): self.skip = False
        if tag in ('p','br','div','h1','h2','h3','h4','li'): self.text.append('\n')
    def handle_data(self, data):
        if not self.skip:
            d = data.strip()
            if d: self.text.append(d)

with open(fname, encoding='utf-8') as f:
    content = f.read()
parser = TextExtractor()
parser.feed(content)
text = '\n'.join(parser.text)
with open(fname.replace('.html','_text.txt'), 'w', encoding='utf-8') as f:
    f.write(text)
```

Read the extracted text files to understand:
- **Format**: numbered sections (一、二、三...), conclusion-first structure, table of contents
- **Style**: uses actual earnings call quotes, specific stock codes (e.g. 光洋科（1785）), supply chain maps
- **Depth**: ~40–46 min read, covers demand/supply/supply chain/company analysis/references
- **Chart convention**: `【圖表：...資料來源：...自行整理】` marks where charts go

Clean up extracted text files after reading.

---

## Step 2: Topic Selection (if no topic given)

Dispatch **3 parallel research agents** (use Task tool with `run_in_background: true`) to evaluate candidate topics:

**Evaluation criteria per topic:**
1. **Niche-ness (1-10)**: Zero Bloomberg/Reuters coverage = 10. Already on CMoney = 3.
2. **Taiwan supply chain depth (1-10)**: Named, investable Taiwan-listed companies
3. **Timeline realism (1-10)**: Must have concrete catalysts in 1-3 years
4. **Research difficulty**: Higher barrier = better moat. Must require IEDM papers, commodity reports, vendor product pages — not just Bloomberg summaries

**Good topic characteristics:**
- Macro trend everyone knows (AI, deglobalization) + enabling sub-technology almost nobody knows
- Supply chain gap: the important piece that's invisible in financial media
- "Picks and shovels" angle — not the headline stock, but the upstream enabler
- Shocking number that requires cross-referencing non-obvious sources

**Agent prompt template:**
> Research whether [TOPIC] is niche enough for 上游洞見. Score it 1-10 on: niche-ness, Taiwan supply chain depth, 1-3yr timeline realism, research difficulty. Find specific Taiwan companies (with stock codes), named catalysts, and assess how hard information is to find. Is this genuinely absent from Taiwanese financial media?

Wait for all 3 agents. If ≥2 independently converge on the same topic, that's the strongest signal. Pick the highest-scoring topic.

**Save topic decision + rationale to a markdown file** before proceeding.

---

## Step 3: Deep Research (Parallel Agents)

Once topic is chosen, dispatch **3-4 parallel research agents** covering:

1. **Technology & international companies**: Technical papers (IEDM, VLSI, SPIE, IEEE), vendor product pages, earnings call quotes from key companies
2. **Taiwan supply chain**: Named Taiwan companies, stock codes, MOPS filings, DigiTimes reports, earnings call mentions
3. **Market data & demand**: Market size forecasts (specialist sources: TECHCET, SFA Oxford, USGS, Yole, LightCounting), pricing, supply/demand math

**Non-obvious source types to always check:**
- Academic conference proceedings (IEDM, IITC, VLSI Symposium, SPIE Lithography)
- Commodity specialist reports (SFA Oxford, USGS MCS, Johnson Matthey PGM reports)
- Vendor product pages and white papers (often ahead of press by 12+ months)
- Specialist blogs (BALD Engineering for ALD, Semiconductor Engineering, Vik's Newsletter)
- TECHCET, DigiTimes (Chinese), 工商時報, 公開資訊觀測站 (MOPS)

**Be honest about what can't be confirmed.** Unconfirmed roles should be labeled "can't confirm from public sources, check MOPS / contact IR."

Wait for all agents to complete, then synthesize.

---

## Step 4: Write the Report

Write in **Traditional Chinese** following 上游洞見 format:

### Required structure:
```
# [Report Title]

> 投資理財內容聲明...（boilerplate）

## 目錄（Table of Contents）

## 一、結論
- Investment thesis FIRST — key Taiwan stocks + international stocks
- Honest assessment of supply chain roles (confirmed vs. probable vs. absent)

## 二、需求面（Demand）
- Why this technology is needed (physics/economics reasoning from first principles)
- Quantified demand drivers

## 三、技術背景（Technology）
- Explain the technology from first principles
- Key components, competing approaches, adoption sequence

## 四、供給面（Supply）
- Where raw materials/IP come from
- Supply constraints and geopolitical risks
- Original supply/demand calculations where possible

## 五、供應鏈（Supply Chain Map）
- Full chain from upstream to end-customer
- Mark Taiwan's position honestly

## 六、時程路線圖（Timeline）
- Node-by-node or year-by-year catalyst table

## 七、台廠介紹（Taiwan Companies）
- Conclusion box first (like HAMR report)
- Each company: 公司介紹 → 具體角色 → 財務表現 → 關注重點
- Include stock codes. Be honest: "confirmed" vs "probable" vs "not confirmed"

## 八、國際廠商介紹（International Companies）
- Same structure per company
- Include specific earnings call quotes with attribution

## 九、參考來源（References）
- All sources with URLs
- Include conference papers, commodity reports, vendor pages
```

### Chart placeholder format:
```
【圖表：[description of what chart shows]
[data that would go in chart]
資料來源：[sources]；自行整理】
```

Place chart placeholders wherever a chart would strengthen the argument (comparisons, timelines, supply maps, price histories).

### Quality checklist before finishing:
- [ ] Conclusion is front-loaded (投資論點前置)
- [ ] At least one original calculation not found elsewhere (e.g., supply/demand math)
- [ ] Specific earnings call quotes with attribution (CEO name, quarter)
- [ ] Honest about what is "confirmed" vs "probable" for Taiwan supply chain roles
- [ ] Chart placeholders in all logical places
- [ ] References include non-obvious sources (conference papers, commodity reports)

---

## Step 5: Generate PDF

```python
import markdown, pathlib

md_path = 'PATH_TO_REPORT.md'
with open(md_path, encoding='utf-8') as f:
    md_text = f.read()
html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
css = '''body{font-family:"Microsoft JhengHei","PingFang TC",serif;font-size:11pt;line-height:1.8;color:#1a1a1a;padding:0 2cm;max-width:900px;margin:auto}h1{font-size:20pt;font-weight:700;margin:1em 0 .4em;border-bottom:3px solid #111;padding-bottom:6px}h2{font-size:15pt;font-weight:700;margin:1.4em 0 .5em;border-bottom:1.5px solid #555;padding-bottom:4px}h3{font-size:12.5pt;font-weight:700;margin:1em 0 .3em;color:#222}h4{font-size:11pt;font-weight:700;margin:.8em 0 .2em;color:#444}p{margin:.5em 0}ul,ol{margin:.4em 0 .4em 1.6em}li{margin:.2em 0}table{border-collapse:collapse;width:100%;margin:.8em 0;font-size:9.5pt}th{background:#222;color:white;padding:5px 8px;text-align:left}td{border:1px solid #ccc;padding:4px 8px}tr:nth-child(even) td{background:#f8f8f8}code,pre{font-family:Consolas,monospace;font-size:9pt;background:#f0f0f0;padding:2px 5px;border-radius:2px}blockquote{border-left:3px solid #aaa;margin:.6em 0 .6em 1em;padding:4px 1em;color:#555;font-size:10pt}hr{border:none;border-top:1px solid #ddd;margin:1em 0}'''
html = f'<!DOCTYPE html><html lang="zh-TW"><head><meta charset="utf-8"><style>{css}</style></head><body>{html_body}</body></html>'
tmp_html = md_path.replace('.md', '_tmp.html')
with open(tmp_html, 'w', encoding='utf-8') as f:
    f.write(html)
```

Then use Chrome headless to render:
```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless=new --disable-gpu --no-sandbox \
  --print-to-pdf="OUTPUT.pdf" \
  --print-to-pdf-no-header \
  "file:///TMP_HTML_PATH" 2>/dev/null
rm TMP_HTML_PATH
```

---

## Notes

- Always work in Traditional Chinese (繁體中文)
- The 上游洞見 style prioritizes: "picks and shovels" angle, niche supply chain, Taiwan-listed companies, law-of-physics reasoning for demand, honest uncertainty disclosure
- A good report is typically 60–80KB markdown, 40+ min read, 40+ references
- Save a handoff markdown if context runs out before report is done
- Use `py` (not `python3`) on this Windows machine
