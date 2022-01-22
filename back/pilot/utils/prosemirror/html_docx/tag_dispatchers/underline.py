from pilot.utils.prosemirror.html_docx.tag_dispatchers import TagDispatcher, replace_whitespaces


class UnderlineDispatcher(TagDispatcher):
    @classmethod
    def append_head(cls, element, container):
        return cls._append_underline(element.text, element, container)

    @classmethod
    def append_tail(cls, element, container):
        return cls._append_underline(element.tail, element, container)

    @classmethod
    def _append_underline(cls, text, element, container):
        """
        <u> Creates an underlined text run inside the paragraph container.
        Appends remainder of text as a additional run
        """
        text = replace_whitespaces(text)
        run = container.add_run(text=text)
        run.underline = True
        return container
