from pilot.utils.prosemirror.html_docx.tag_dispatchers import TagDispatcher, replace_whitespaces


class StrikeDispatcher(TagDispatcher):
    @classmethod
    def append_head(cls, element, container):
        return cls._append_strike(element.text, element, container)

    @classmethod
    def append_tail(cls, element, container):
        return cls._append_strike(element.tail, element, container)

    @classmethod
    def _append_strike(cls, text, element, container):
        """
        <s> Creates a strike text run inside the paragraph container.
        Appends remainder of text as a additional run
        """
        text = replace_whitespaces(text)
        run = container.add_run(text=text)
        run.font.strike = True
        return container
