# PDF 生成流程（Windows + Chrome Headless）

## Step 1: Markdown → HTML

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

## Step 2: HTML → PDF

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless=new --disable-gpu --no-sandbox \
  --print-to-pdf="OUTPUT.pdf" \
  --print-to-pdf-no-header \
  "file:///TMP_HTML_PATH" 2>/dev/null
rm TMP_HTML_PATH
```

## 注意事項

- 使用 `py`（不是 `python3`）執行 Python
- 需要安裝 `markdown` 套件（`pip install markdown`）
- CSS 已針對上游洞見報告風格優化
- Chrome headless 路徑為 Windows 預設安裝位置
