"""從 HTML 報告中提取純文字內容。用於解析過去的參考報告。"""

from html.parser import HTMLParser
import sys


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'head'):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'head'):
            self.skip = False
        if tag in ('p', 'br', 'div', 'h1', 'h2', 'h3', 'h4', 'li'):
            self.text.append('\n')

    def handle_data(self, data):
        if not self.skip:
            d = data.strip()
            if d:
                self.text.append(d)


def extract(fname: str) -> str:
    with open(fname, encoding='utf-8') as f:
        content = f.read()
    parser = TextExtractor()
    parser.feed(content)
    return '\n'.join(parser.text)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: py html_extractor.py <file.html>")
        sys.exit(1)
    text = extract(sys.argv[1])
    out = sys.argv[1].replace('.html', '_text.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Extracted to {out}")
