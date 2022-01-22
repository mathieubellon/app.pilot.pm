from pilot.utils.prosemirror.html_docx.tag_dispatchers import TagDispatcher, replace_whitespaces


class DivDispatcher(TagDispatcher):
    @classmethod
    def append_head(cls, element, container):
        div = cls.get_new_paragraph(container)
        return cls._append_div(element.text, element, div)

    @classmethod
    def append_tail(cls, element, container):
        div = cls.get_current_paragraph(container)
        return cls._append_div(element.tail, element, div)

    @classmethod
    def _append_div(cls, text, element, container):
        """
        <div> creates a div element inside a docx container element.
        """
        text = replace_whitespaces(text).strip()

        style = None
        cls = list(element.classes)

        if 'field_label_left' in cls:
            text = text.strip()
            style = 'LabelField'

        text = replace_whitespaces(text)
        if not text:
            return container

        container.text = text
        container.style = style
        return container
