from collections import namedtuple

from pilot.utils.prosemirror.prosemirror import prosemirror_json_to_html, prosemirror_json_to_markdown, \
    prosemirror_json_to_text


class SerializationFormat:
    RAW = 'raw'
    HTML = 'html'
    TEXT = 'text'
    MARKDOWN = 'markdown'


Dialect = namedtuple('Dialect', ['format', 'newline', 'pm_converter', 'link_serializer'])


def text_link(href, text):
    return href


def html_link(href, text):
    return f'<a href="{href}">{text}</a>'


def markdown_link(href, text):
    return f'[{href}]({text})'


class SerializationDialect:
    TEXT = Dialect(SerializationFormat.TEXT, '\n', prosemirror_json_to_text, text_link)
    HTML = Dialect(SerializationFormat.HTML, '<br />', prosemirror_json_to_html, html_link)
    MARKDOWN = Dialect(SerializationFormat.MARKDOWN, '\n', prosemirror_json_to_markdown, markdown_link)

    DIALECTS = (TEXT, HTML, MARKDOWN)
    DIALECTS_DICT = {dialect.format: dialect for dialect in DIALECTS}


def get_dialect(format):
    if format not in SerializationDialect.DIALECTS_DICT:
        raise ValueError(f'Unknown serialization format : "{format}"')
    return SerializationDialect.DIALECTS_DICT[format]
