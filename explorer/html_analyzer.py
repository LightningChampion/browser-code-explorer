from __future__ import annotations

from html.parser import HTMLParser


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.title = ""
        self.h1 = ""
        self.links = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.current = tag

        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if self.current == tag:
            self.current = None

    def handle_data(self, data):
        data = data.strip()

        if not data:
            return

        if self.current == "title":
            self.title += data
        elif self.current == "h1" and not self.h1:
            self.h1 = data
        elif self.current in {"p", "li"}:
            self.text.append(data)


class HtmlAnalyzer:
    def analyze(self, html: str) -> dict:
        parser = PageParser()
        parser.feed(html)

        return {
            "title": parser.title,
            "heading": parser.h1,
            "links": parser.links,
            "summary": " ".join(parser.text[:5]),
        }
