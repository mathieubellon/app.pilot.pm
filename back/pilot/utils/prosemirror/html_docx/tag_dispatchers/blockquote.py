from pilot.utils.prosemirror.html_docx.tag_dispatchers import TagDispatcher


class BlockquoteDispatcher(TagDispatcher):
    @classmethod
    def append_head(cls, element, container):
        return cls._append_blockquote(container)

    @classmethod
    def append_tail(cls, element, container):
        return cls._append_blockquote(container)

    @classmethod
    def _append_blockquote(cls, container):
        """
        <blockquote> creates a quote styled paragraph inside a docx container element.
        """
        return container
