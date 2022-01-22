<template>
<div class="RichTextEditor">
    <RichTextMenuBar
        :annotationManager="annotationManager"
        :canFade="menuBarCanFade"
        :editor="editor"
        :excludeMenuBarItems="excludeMenuBarItems"
        :readOnly="readOnly"
    />
    <EditorContent
        class="RichTextStyling px-4"
        ref="editorContent"
        :editor="editor"
    />
</div>
</template>

<script>
import { EditorContent, EditorMenuBar } from "tiptap"

import RichTextMenuBar from "./RichTextMenuBar"

export default {
    name: "RichTextEditor",
    components: {
        EditorContent,
        EditorMenuBar,
        RichTextMenuBar,
    },
    props: {
        editor: {
            type: Object,
            required: true,
        },
        annotationManager: Object,
        excludeMenuBarItems: Array,
        readOnly: {
            type: Boolean,
            default: false,
        },
        menuBarCanFade: {
            type: Boolean,
            default: false,
        },
    },
}
</script>
