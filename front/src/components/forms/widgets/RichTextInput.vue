<template>
<RichTextEditor
    :editor="editor"
    :excludeMenuBarItems="excludeMenuBarItems"
/>
</template>

<script>
import _ from "lodash"
import { Editor } from "tiptap"
import { EMPTY_PROSEMIRROR_DOC, richTextSchema } from "@richText/schema"
import { removeEmptyParagraphsFromSlice } from "@richText/cleaning"
import RichTextEditor from "@richText/RichTextEditor"

export default {
    name: "RichTextInput",
    components: {
        RichTextEditor,
    },
    props: {
        value: Object,
        placeholder: String,
        excludeMenuBarItems: Array,
        editorSchema: {
            default: () => richTextSchema,
        },
    },
    data: () => ({
        editor: null,
    }),
    methods: {
        onUpdate({ getJSON }) {
            this.$emit("input", getJSON())
        },
    },
    watch: {
        value(newValue) {
            if (!_.isEqual(newValue, this.editor.getJSON())) {
                this.editor.setContent(newValue)
            }
        },
    },
    created() {
        let editorSchema = this.editorSchema || richTextSchema
        let value = this.value
        if (_.isEmpty(value)) {
            value = EMPTY_PROSEMIRROR_DOC
        }

        let editorProps = {
            transformPasted: removeEmptyParagraphsFromSlice,
        }
        if (this.placeholder) {
            editorProps.placeholder = this.placeholder
        }

        this.editor = new Editor({
            content: value,
            extensions: editorSchema.getExtensions(),
            onUpdate: this.onUpdate,
            serializer: editorSchema.DOMSerializer,
            injectCSS: false,
            editorProps,
        })
        // Convert value prop entered as HTML into a proper prosemirror doc
        if (_.isString(this.value)) {
            this.$emit("input", this.editor.getJSON())
        }
    },
    beforeDestroy() {
        this.editor.destroy()
    },
}
</script>

<style lang="scss"></style>
