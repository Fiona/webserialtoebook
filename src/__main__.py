"""Web Serial To eBook

Usage:
  ./webserialtoebook list
  ./webserialtoebook pages SERIAL
  ./webserialtoebook fetch SERIAL
"""
import argparse
import os.path
import pkgutil
import sys

from ebooklib import epub

VERSION = "0.1"


def supported_serials():
    """Gets a list of supported serials as short names"""
    return [name for _, name, _ in pkgutil.iter_modules(["serials"]) if name != "base"]


def get_serial_object(serial_name):
    """Imports and creates the web serial definition object."""
    serial_module = __import__(
        f"serials.{serial_name}",
        globals(),
        locals(),
        ['serial'],
        0
    )
    return serial_module.serial()


def task_list(parsed_args):
    """List supported web serials"""
    print("Supported web serials -\n")
    for name in supported_serials():
        serial = get_serial_object(name)
        print(f"{name} - {serial.name} by {serial.author} ({serial.homepage})")


def task_pages(parsed_args):
    """Show list of pages/chapters of a web serial"""
    try:
        serial = get_serial_object(parsed_args.serial)
    except ImportError:
        print(f"Serial '{parsed_args.serial}' not supported.")
        return
    pages = serial.get_pages()
    print(f"Pages in {serial.name} by {serial.author}\n")
    for title, url in pages:
        print(f"{title} ({url})")


def task_fetch(parsed_args):
    """Gets and stores all pages of a web serial"""
    try:
        serial = get_serial_object(parsed_args.serial)
    except ImportError:
        print(f"Serial '{parsed_args.serial}' not supported.")
        return
    # Create the dir structure
    pages_path = os.path.join(os.sep, "tmp", "out", parsed_args.serial)
    if not os.path.exists(pages_path):
        os.mkdir(pages_path)
    # Get pages to fetch
    pages = serial.get_pages()
    # Cleaning if required
    if parsed_args.clean:
        print("Deleting cached pages...")
        for page_num, page in enumerate(pages):
            page_file_path = os.path.join(pages_path, f"{page_num}.html")
            if os.path.exists(page_file_path):
                os.remove(page_file_path)
    print(f"Fetching {len(pages)} pages...")
    for page_num, page in enumerate(pages):
        if parsed_args.limit is not None and page_num >= parsed_args.limit:
            break
        title, url = page
        page_file_path = os.path.join(pages_path, f"{page_num}.html")
        print(f"Fetching \"{title}\"...")
        if os.path.exists(page_file_path):
            print("Exists, skipping.")
            continue
        page_content = serial.get_content_from_page(url)
        page_file_content = f"<html><head></head><body><h1>{title}</h1>{page_content}</body></html>"
        with open(page_file_path, "w") as fh:
            fh.write(page_file_content)
        local_file_path = page_file_path.partition("/tmp/")[2]
        print(f"Saved to {local_file_path}.")
    print("Done fetching all pages!")


def task_compile(parsed_args):
    """Collects previously fetched pages of a serial and compiles them into an epub file for use on ebook readers."""
    try:
        serial = get_serial_object(parsed_args.serial)
    except ImportError:
        print(f"Serial '{parsed_args.serial}' not supported.")
        return
    # Create the dir structure
    pages_path = os.path.join(os.sep, "tmp", "out", parsed_args.serial)
    if not os.path.exists(pages_path):
        print(f"Serial pages directory '{pages_path}' does not exist.")
        print(f"Have you ran './webserialtoebook fetch {parsed_args.serial}'?")
        return
    # Get pages to compile
    pages = serial.get_pages()
    print(f"Checking {len(pages)} pages exist...")
    for page_num, page in enumerate(pages):
        page_file_path = os.path.join(pages_path, f"{page_num}.html")
        if not os.path.exists(page_file_path):
            print(f"Page file {page_file_path} does not exist. Please ensure you have fetched the entire serial.")
            return
    # Set metadata for epub
    book = epub.EpubBook()
    book.set_identifier(parsed_args.serial)
    book.set_title(serial.name)
    book.set_language("en")
    book.add_author(serial.author)
    # Collate pages
    toc = []
    print("Collating pages...")
    for page_num, page in enumerate(pages):
        title, url = page
        page_file_path = os.path.join(pages_path, f"{page_num}.html")
        ebook_page = epub.EpubHtml(title=title, file_name=f"{page_num}.xhtml")
        with open(page_file_path, "r") as fh:
            ebook_page.set_content(fh.read())
        toc.append(ebook_page)
        book.add_item(ebook_page)
    book.toc = toc
    book.spine = toc
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    # Write out
    print("Writing epub...")
    epub_file_path = os.path.join(os.sep, "tmp", "out", f"{parsed_args.serial}.epub")
    epub.write_epub(epub_file_path, book)
    local_file_path = epub_file_path.partition("/tmp/")[2]
    print(f"Finished compiling {serial.name} by {serial.author} to {local_file_path}")


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(description='Web Serial to Ebook')
    subparsers = main_parser.add_subparsers(help='Available commands')

    parser_1 = subparsers.add_parser('list', help='List web serials supported.')
    parser_1.set_defaults(func=task_list)

    parser_2 = subparsers.add_parser('pages',
                                     help='List the pages/chapters of a web serial. Pass a serial name (ie: pages worm).')
    parser_2.set_defaults(func=task_pages)
    parser_2.add_argument("serial")

    parser_3 = subparsers.add_parser('fetch',
                                     help='Get contents of a serial and store it locally. Pass a serial name (ie: fetch worm).')
    parser_3.set_defaults(func=task_fetch)
    parser_3.add_argument("serial")
    parser_3.add_argument("--limit", type=int, help='Limit the number of pages to fetch.')
    parser_3.add_argument("--clean", action="store_true", help="Remove all cached pages and get from scratch.")

    parser_3 = subparsers.add_parser('compile',
                                     help='Combine together previously a fetched serial into an epub file. Pass a serial name (ie: fetch worm).')
    parser_3.set_defaults(func=task_compile)
    parser_3.add_argument("serial")

    if len(sys.argv[1:]) == 0:
        main_parser.print_help()
        main_parser.exit()
    args = main_parser.parse_args()
    args.func(args)
