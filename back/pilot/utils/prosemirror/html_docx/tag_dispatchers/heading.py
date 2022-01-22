from pilot.utils.prosemirror.html_docx.tag_dispatchers import TagDispatcher


class HeadingDispatcher(TagDispatcher):
    @classmethod
    def append_head(cls, element, container):
        paragraph = cls.get_new_paragraph(container)
        return cls._append_heading(element.text, element.tag, paragraph)

    @classmethod
    def append_tail(cls, element, container):
        paragraph = cls.get_current_paragraph(container)
        return cls._append_heading(element.tail, element.tag, paragraph)

    @classmethod
    def _append_heading(cls, text, tag, container):
        """
        <hx> Creates a heading paragraph inside the document container
        """
        try:
            level = int(tag[1:])
            style = 'Title' if level == 0 else 'HEADING_%d' % level
        except ValueError:
            style = None
            text = "\nBROKEN, CANNOT INCLUDE ELEMENTS IN HEADINGS (%s)\n" % text

        container.text = text
        container.style = style
        return container
