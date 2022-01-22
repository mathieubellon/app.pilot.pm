<template>
<div class="w-64 p-2">
    <button
        class="menu-item flex-col items-start"
        @click="clean()"
    >
        <span>{{ $t("clean") }}</span>
        <span class="menu-item-description">{{ $t("cleanDescription") }}</span>
    </button>

    <button
        class="menu-item flex-col items-start"
        @click="showFormatted('plainText')"
    >
        <span>{{ $t("seePlainText") }}</span>
        <span class="menu-item-description">{{ $t("seePlainTextDescription") }}</span>
    </button>

    <button
        class="menu-item flex-col items-start"
        @click="showFormatted('markdown')"
    >
        <span>{{ $t("seeMarkdown") }}</span>
        <span class="menu-item-description">{{ $t("seeMarkdownDescription") }}</span>
    </button>

    <button
        class="menu-item flex-col items-start"
        @click="showFormatted('html')"
    >
        <span>{{ $t("seeHtml") }}</span>
        <span class="menu-item-description">{{ $t("seeHtmlDescription") }}</span>
    </button>

    <div ref="formattedContentModal">
        <Modal
            height="80%"
            :maxWidth="1000"
            :name="`formattedContent-${editorId}`"
            width="80%"
        >
            <div class="p-6 h-full flex flex-col">
                <div class="flex justify-between">
                    <span
                        v-if="this.format"
                        class="font-bold"
                    >
                        {{ $t("display") }} {{ $t("format." + this.format) }}
                    </span>

                    <div>
                        <span
                            v-if="copiedToClipboard"
                            class="text-green-600 font-bold mr-2"
                        >
                            ✓ {{ $t("okCopied") }}
                        </span>
                        <button
                            class="button is-indigo mb-2"
                            @click="copyToClipboard"
                        >
                            {{ $t("copyToClipboard") }}
                        </button>
                    </div>
                </div>

                <textarea
                    class="flex-grow"
                    ref="formattedContentTextarea"
                    :readOnly="true"
                    :value="formattedValue"
                />
            </div>
        </Modal>
    </div>
</div>
</template>

<script>
import $ from "jquery"
import { cleanEmptyParagraphs } from "@/richText/cleaning"
import { serializeDocToHTML } from "@/richText/utils"

import { itemContentSchema } from "@/richText/schema"

export default {
    name: "RichTextMenuBarOptionsMenu",
    inject: ["editorId"],
    props: {
        editor: {
            type: Object,
            required: true,
        },
    },
    data: () => ({
        format: null,
        copiedToClipboard: false,
    }),
    computed: {
        formattedValue() {
            // HTML value
            if (this.format == "html") {
                return serializeDocToHTML(this.editor, "\n\n")
            }
            // Markdown value
            if (this.format == "markdown") {
                return itemContentSchema.MarkdownSerializer.serialize(this.editor.state.doc)
            }
            // Plain text value
            if (this.format == "plainText") {
                let doc = this.editor.state.doc
                return doc.textBetween(0, doc.content.size, "\n\n")
            }
            return ""
        },
    },
    methods: {
        clean() {
            cleanEmptyParagraphs(this.editor)
        },
        showFormatted(format) {
            this.format = format
            this.$modal.show(`formattedContent-${this.editorId}`)
        },
        copyToClipboard() {
            let textarea = this.$refs.formattedContentTextarea
            textarea.select()
            document.execCommand("copy")
            textarea.selectionEnd = 0
            this.copiedToClipboard = true
        },
    },
    mounted() {
        // Move the modal out of the menubar to fix z-index + position:sticky issues
        $(this.$refs.formattedContentModal).appendTo("body")
    },
    beforeDestroy() {
        this.$modal.hide(`formattedContent-${this.editorId}`)

        // Elements appended to body must be removed manually, because Vue.js won't do it automatically.
        if (this.$refs.formattedContentModal) {
            this.$refs.formattedContentModal.remove()
        }
    },
    i18n: {
        messages: {
            fr: {
                clean: "Nettoyer le texte",
                cleanDescription:
                    "Réalise plusieurs opérations sur le texte comme la suppression de paragraphes vides. Utile après un copié-collé depuis Word.",
                copyToClipboard: "Copier dans le presse-papier",
                display: "Affichage",
                format: {
                    html: "html",
                    markdown: "markdown",
                    plainText: "plein texte",
                },
                okCopied: "Ok, copié",
                seeHtml: "Afficher en html",
                seeHtmlDescription: "Afficher en html",
                seeMarkdown: "Afficher en markdown",
                seeMarkdownDescription:
                    "Affiche le texte au format markdown. Pratique pour copier-coller vers des outils de génération de sites statiques ou Wordpress",
                seePlainText: "Afficher en texte brut",
                seePlainTextDescription: "Afficher en texte brut",
            },
            en: {
                clean: "Clean texte",
                copyToClipboard: "Copy to clipboard",
                display: "Display",
                format: {
                    html: "html",
                    markdown: "markdown",
                    plainText: "plain texte",
                },
                okCopied: "Ok, copied",
                seeHtml: "See html",
                seeHtmlDescription: "See html",
                seeMarkdown: "See markdown",
                seeMarkdownDescription: "See markdown",
                seePlainText: "See plain text",
                seePlainTextDescription: "See plain text",
            },
        },
    },
}
</script>
