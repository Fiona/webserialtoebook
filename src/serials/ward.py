import re

import mechanicalsoup

from .base import BaseWebSerial


class WardWebSerial(BaseWebSerial):
    name = "Ward"
    author = "J.C. McCrae"
    homepage = "https://www.parahumans.net"

    toc_path = "/table-of-contents/"
    browser = None

    def get_pages(self):
        self.browser = mechanicalsoup.StatefulBrowser()
        self.browser.open(self.homepage + self.toc_path)
        soup = self.browser.page
        pages = []
        for toc_menu in ["nav_menu-5", "nav_menu-6"]:
            for arc_list_tag in soup.select(f"aside section#{toc_menu} li.menu-item-has-children"):
                arc_title_tag = arc_list_tag.find("a")
                full_arc_title = arc_title_tag.get_text().strip()
                current_arc = re.match(r"Arc (\d+|X) \((.*)\)", full_arc_title).group(2)
                pages_tags = arc_list_tag.ul.find_all("li")
                for page_tag in pages_tags:
                    page_title = page_tag.get_text().strip()
                    complete_page_title = f"{current_arc}: {page_title}"
                    pages.append((complete_page_title, self.homepage + page_tag.a["href"]))
        return pages

    def get_content_from_page(self, page_url):
        self.browser = mechanicalsoup.StatefulBrowser()
        self.browser.open(page_url)
        soup = self.browser.page
        content = []
        paragraphs = soup.select(f"article div.entry-content p")
        # Skip the initial preamble from the first page
        if "/glow-worm-0-1/" in page_url:
            paragraphs = paragraphs[6:]
        for paragraph in paragraphs:
            links = paragraph.find_all("a")
            for link in links:
                link.extract()
            if not paragraph.get_text().strip():
                continue
            content.append(str(paragraph))
        return "".join(content)

serial = WardWebSerial
