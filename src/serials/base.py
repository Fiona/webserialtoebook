
class BaseWebSerial:
    name = "Web Serial Name"
    author = "Web Serial Author"
    homepage = "http://www.example.com"

    def get_pages(self):
        """Returns a list of tuples containing chapter tiles and page urls."""
        return [
            ("Chapter 1", "http://www.example.com/chapter-1/"),
            ("Chapter 2", "http://www.example.com/chapter-2/"),
        ]

    def get_content_from_page(self, page_url):
        return "<p>Page content</p>"