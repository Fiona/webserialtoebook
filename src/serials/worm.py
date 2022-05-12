import re
from urllib import request
from urllib import parse

from bs4 import BeautifulSoup

from .base import BaseWebSerial


class WormWebSerial(BaseWebSerial):
    name = "Worm"
    author = "J.C. McCrae"
    homepage = "https://parahumans.wordpress.com/"

    toc_path = "table-of-contents/"

    def get_pages(self):
        req = request.Request(self.homepage + self.toc_path)
        content = request.urlopen(req).read()
        soup = BeautifulSoup(content, "html.parser")
        pages = []
        current_arc = ""
        for page_tag in soup.select("article div.entry-content strong"):
            page_name = page_tag.get_text().strip()
            # Skip some accidental empty hyperlinks
            if not page_name:
                continue
            # Some arc titles aren't wrapped properly, very frustrating
            bad_arc_titles = [
                ("Arc 17", "Migration"), ("Arc 18", "Queen"), ("Arc 21", "Imago"),
                ("Arc 22", "Cell"), ("Arc 25", "Scarab"), ("Arc 27", "Extinction"), ("Arc 30", "Speck"),
                ("Epilogue: Teneral", "Epilogue: Teneral"), ("Sequel Teaser Chapters", "Glow-worm"),
            ]
            for bad_arc_num, bad_arc_title in bad_arc_titles:
                if page_name.startswith(bad_arc_num):
                    current_arc = bad_arc_title
                    break
            # Pages that aren't URLs are usually arc titles
            page_url_tags = page_tag.find_all("a")
            if not len(page_url_tags):
                # Some of the arc titles wrap the A in "Arc", lmao
                if page_name == "A":
                    continue
                # Teneral E.2 is not linked on the TOC, very annoying. Hardcoding it here.
                if page_name == "E.2":
                    full_page_name = f"{current_arc}: {page_name}"
                    pages.append((full_page_name, "https://parahumans.wordpress.com/2013/11/05/teneral-e-2/"))
                    continue
                # Some hilarious page entries swap the nesting order of strong/a tags, so need to accommodate for them
                if re.match(r"(\d+|E|P)\.(\d+|x|y|z|a|b).*", page_name):
                    page_url_tags = [page_tag.find_parent("a")]
                else:
                    # Pull out the arc name only
                    current_arc = re.match(r"(Arc|rc) \d+: (.*)", page_name).group(2)
                    continue
            # Most pages are just singular links
            if len(page_url_tags) == 1:
                page_name = page_url_tags[0].get_text().strip()
                # One url is missing the https
                if not page_url_tags[0]["href"].startswith("https"):
                    page_url_tags[0]["href"] = "https://"+page_url_tags[0]["href"]
                page = (f"{current_arc}: {page_name}", self.clean_url(page_url_tags[0]["href"]))
                if not page in pages:
                    pages.append(page)
                continue
            # Some pages are weird and have multiple links in the same strong tags
            for page_url_tag in page_url_tags:
                page_name = page_url_tag.get_text().strip()
                if not page_name:
                    continue
                page = (f"{current_arc}: {page_name}", self.clean_url(page_url_tag["href"]))
                if not page in pages:
                    pages.append(page)
        return pages

    def get_content_from_page(self, page_url):
        req = request.Request(page_url)
        content = request.urlopen(req).read()
        soup = BeautifulSoup(content, "html.parser")
        content = []
        for paragraph in soup.select("article div.entry-content p"):
            links = paragraph.find_all("a")
            for link in links:
                link.extract()
            if not paragraph.get_text().strip():
                continue
            content.append(str(paragraph))
        return "".join(content)

    def clean_url(self, url):
        scheme, netloc, path, query, fragment = parse.urlsplit(url)
        path = parse.quote(path)
        return parse.urlunsplit((scheme, netloc, path, query, fragment))


serial = WormWebSerial
