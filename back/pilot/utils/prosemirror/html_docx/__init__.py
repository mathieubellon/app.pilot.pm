from lxml.html import fromstring
from pilot.utils.prosemirror.html_docx.converter import DocxBuilder

__doc__ = """
Wrapper methods used for mapping HTML to docx objects.
https://github.com/fokoenecke/html_docx/

Modified version for Pilot.
"""


def add_html(container, html_string):
    # fromstring() doesn't like empty strings, convert them to an empty paragraph
    if not html_string:
        html_string = '<p></p>'
    root = fromstring(html_string)
    builder = DocxBuilder(container=container)
    builder.from_html_tree(root=root)
