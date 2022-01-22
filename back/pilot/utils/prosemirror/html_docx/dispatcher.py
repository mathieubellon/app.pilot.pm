"""
Returns corresponding objects to call for creating
the different docx elements.
"""

from pilot.utils.prosemirror.html_docx.tag_dispatchers.blockquote import BlockquoteDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.code import CodeDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.emphasis import EmphasisDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.heading import HeadingDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.linebreak import LineBreakDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.link import LinkDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.list_item import ListItemDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.paragraph import ParagraphDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.div import DivDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.strong import StrongDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.strike import StrikeDispatcher
from pilot.utils.prosemirror.html_docx.tag_dispatchers.underline import UnderlineDispatcher


def get_tag_dispatcher(html_tag):
    """
    Returning the object creating OOXML for the given HTML tag
    """
    return _dispatch_html.get(html_tag)


# map of HTML tags and their corresponding objects
heading_dispatcher = HeadingDispatcher()

_dispatch_html = dict(
    div=DivDispatcher(),
    p=ParagraphDispatcher(),
    a=LinkDispatcher(),
    li=ListItemDispatcher(),
    br=LineBreakDispatcher(),
    code=CodeDispatcher(),
    strong=StrongDispatcher(),
    em=EmphasisDispatcher(),
    u=UnderlineDispatcher(),
    s=StrikeDispatcher(),
    h1=heading_dispatcher,
    h2=heading_dispatcher,
    h3=heading_dispatcher,
    h4=heading_dispatcher,
    h5=heading_dispatcher,
    h6=heading_dispatcher,
    blockquote=BlockquoteDispatcher(),
)
