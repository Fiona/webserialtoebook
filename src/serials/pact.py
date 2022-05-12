import re

import mechanicalsoup

from .base import BaseWebSerial


class PactWebSerial(BaseWebSerial):
    name = "Pact"
    author = "J.C. McCrae"
    homepage = "https://pactwebserial.wordpress.com"

    toc_path = "/table-of-contents/"
    browser = None

    def get_pages(self):
        self.browser = mechanicalsoup.StatefulBrowser()
        self.browser.open(self.homepage + self.toc_path)
        soup = self.browser.page
        pages = []
        for arc_list_tag in soup.select(f"aside#categories-2 > nav > ul > li.cat-item > ul.children > li.cat-item"):
            arc_title_tag = arc_list_tag.find("a")
            current_arc = arc_title_tag.get_text().strip()
            if current_arc == "Epilogue":
                pages.append((current_arc, arc_title_tag["href"]))
                continue
            current_arc = re.match(r"Arc (\d+|X) \((.*)\)", current_arc).group(2)
            pages_tags = arc_title_tag.find_next_sibling("ul").select("li > a")
            for page_tag in pages_tags:
                page_title = page_tag.get_text().strip()
                complete_page_title = f"{current_arc}: {page_title}"
                pages.append((complete_page_title, page_tag["href"]))
        return pages

    def get_content_from_page(self, page_url):
        self.browser = mechanicalsoup.StatefulBrowser()
        self.browser.open(page_url)
        soup = self.browser.page
        content = []
        for paragraph in soup.select(f"article div.entry-content p"):
            links = paragraph.find_all("a")
            for link in links:
                link.extract()
            if not paragraph.get_text().strip():
                continue
            content.append(str(paragraph))
        return "".join(content)


serial = PactWebSerial