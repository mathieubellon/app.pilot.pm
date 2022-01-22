import os
import json
import logging
import subprocess
import tempfile

from django.utils.safestring import mark_safe

from settings.base import frontend_path

logger = logging.getLogger(__name__)

__doc__ = '''
Rich edited content is stored in Json (Prosemirror Document model)
These tools allow conversion from/to Json Prosemirror Document model
'''

EMPTY_PROSEMIRROR_DOC = {"content": [{"type": "paragraph"}], "type": "doc"}


def get_body_input_as_dict(pm_document):
    """
    Coerce a body value incoming from the user through a django-form or a DRF-serializer

    The body may be a json-encoded string, or a plain python dict.
    This function ensure that the value always end up being a python dict.
    """
    if isinstance(pm_document, str):
        try:
            return json.loads(pm_document)
        except Exception as e:
            logger.error('Json is malformed', exc_info=True)
            raise

    elif isinstance(pm_document, dict):
        return pm_document

    else:
        raise ValueError('body value must either a dict or a json-encoded string')


def convert_text_to_prosemirror_doc(text):
    if not text:
        return {}

    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\n\n', '\n')
    paragraph_nodes = [{"type":"paragraph","content": [{"type":"text", "text": string}]}
                       for string in text.split('\n') if string]
    return {"type": "doc", "content": paragraph_nodes}


def call_nodejs_serialize_prosemirror_document(pm_document, output_format):
    if not pm_document or pm_document == EMPTY_PROSEMIRROR_DOC:
        return ''

    pm_document_dict = get_body_input_as_dict(pm_document)
    pm_document_string = json.dumps(pm_document_dict).encode()
    temporary_file = None

    try:
        # Small documents : pass directly the json as arg
        if len(pm_document_string) < 10000:
            transfer_mode = 'argument'
            argument = json.dumps(pm_document)
        # Document too large : transfer through a temporary file
        else:
            temporary_file = tempfile.NamedTemporaryFile(prefix='prosemirrorJsonToMarkdown_', delete=False)
            temporary_file.write(pm_document_string)
            transfer_mode = 'tempfile'
            argument = temporary_file.name

        serialized_document = subprocess.check_output(
            ['node', frontend_path(os.path.join('serializePmDoc', 'serializePmDoc.js')), argument,  transfer_mode, output_format],
            stderr=subprocess.STDOUT
        )
        serialized_document = serialized_document.decode()

        # Prosemirror serialize to CommonMarkdown which states that line break should be represented with backslash.
        # We do not want that. Replace this after writing our own Python Prosemirror Node Parser/Serializer
        serialized_document = serialized_document.replace('\\\n', '\n')

    except subprocess.CalledProcessError as e:
        logger.error(f'Failed to serialize prosemirror document by node.js. '
                     f'Output below :\n{e.output.decode()}', exc_info=True)
        raise
    except Exception as e:
        logger.error('Failed to serialize prosemirror document', exc_info=True)
        raise
    finally:
        if temporary_file:
            temporary_file.close()

    return serialized_document


def prosemirror_json_to_markdown(pm_document):
    """
    Utility to convert JSON Prosemirror Document format to Markdown
    Warning : This will delegate to Node.js, which may be resource consuming

    Args:
        pm_document: a Json string or python dict representing a Prosemirror document

    Returns: A string formatted in Markdown
    """
    return call_nodejs_serialize_prosemirror_document(pm_document, 'markdown')


def prosemirror_json_to_html(pm_document):
    """
    Utility to convert JSON Prosemirror Document format to html.
    Warning : This will delegate to Node.js, which may be resource consuming

    Args:
        pm_document: a Json string or python dict representing a Prosemirror document

    Returns: A string formatted in html
    """
    html_document = call_nodejs_serialize_prosemirror_document(pm_document, 'html')
    # Prosemirror schema allow paragraph in list item and this exported as HTML "as is"
    # Before we properly fix this let's replace all the things and write too specific code
    html_document = mark_safe(html_document.replace('<li><p>', '<li>').replace('</p></li>','</li>'))
    return html_document


def prosemirror_json_to_text(pm_document):
    """
    Utility to convert JSON Prosemirror Document format to plain text.
    Warning : This will delegate to Node.js, which may be resource consuming

    Args:
        pm_document: a Json string or python dict representing a Prosemirror document

    Returns: A string formatted in plain text
    """
    return call_nodejs_serialize_prosemirror_document(pm_document, 'text')


def get_body_input_as_text(value):
    return prosemirror_json_to_text(get_body_input_as_dict(value))


def get_prosemirror_text_list(node, text_chunks):
    """
    Here we could do without the text_chunks param and return an concatenation of lists,
    but appending to a single list is much faster :-)
    """
    if not node:
        return

    text, content = node.get('text'), node.get('content')

    if text:
        text_chunks.append(text)

    if content:
        for child in content:
            get_prosemirror_text_list(child, text_chunks)


def prosemirror_json_to_search_document(pm_document):
    """
    Utility to extract the plain text content of a JSON Prosemirror Document.
    This is written in python, which is much less consuming than `prosemirror_json_to_text`

    Args:
        pm_document: a Json string or python dict representing a Prosemirror document

    Returns: A string in plain text
    """
    text_list = []
    get_prosemirror_text_list(pm_document, text_list)
    return ' '.join(text_list)


def for_each_mentions(node, callback):
    if isinstance(node, dict):
        marks_list = node.get('marks', [])
        marks = {mark['type']:mark for mark in marks_list}
        if 'mention' in marks:
            callback(node, marks['mention']['attrs'])

        else:
            for value in node.values():
                if isinstance(value, (dict, list)):
                    for_each_mentions(value, callback)
    elif isinstance(node, list):
        for value in node:
            for_each_mentions(value, callback)


def get_mentions_list(node):
    mentions_list = []
    for_each_mentions(node, lambda n, mention: mentions_list.append(mention))
    return mentions_list
