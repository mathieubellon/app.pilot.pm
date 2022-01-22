from pilot.utils.prosemirror.html_docx.tag_dispatchers import TagDispatcher, replace_whitespaces


class ParagraphDispatcher(TagDispatcher):
    @classmethod
    def append_head(cls, element, container):
        paragraph = cls.get_new_paragraph(container)
        return cls._append_paragraph(element.text, element, paragraph)

    @classmethod
    def append_tail(cls, element, container):
        paragraph = cls.get_current_paragraph(container)
        return cls._append_paragraph(element.tail, element, paragraph)

    @classmethod
    def _append_paragraph(cls, text, element, container):
        """
        <p> creates a paragraph element inside a docx container element.
        """
        text = replace_whitespaces(text)
        if not text:
            return container

        style = None
        if element.getparent().tag == 'blockquote':
            style = 'IntenseQuote'

        container.add_run(text=text, style=style)
        return container
