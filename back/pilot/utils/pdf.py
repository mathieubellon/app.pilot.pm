from io import BytesIO

import unicodedata
import xhtml2pdf.pisa as pisa

from django.template.loader import render_to_string


class PdfRenderingException(Exception):
    def __init__(self, message, html):
        super(PdfRenderingException, self).__init__(message)
        self.html = html


def render_to_pdf(template_name, context):
    html = render_to_string(template_name, context)
    # pisa don't handle well unicode decomposition, so we normalize to a composed form
    html = unicodedata.normalize('NFKC', html)
    result = BytesIO()
    pdf = pisa.pisaDocument(html, result)
    if pdf.err:
        raise PdfRenderingException(pdf.err, html)
    return result.getvalue()
