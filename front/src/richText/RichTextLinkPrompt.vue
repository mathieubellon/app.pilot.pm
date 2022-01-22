<template>
<Modal
    height="auto"
    :name="`linkPrompt-${editorId}`"
    @opened="focus()"
>
    <div class="p-8">
        <form
            class="w-full"
            ref="form"
            @keydown.enter.prevent="$emit('submit')"
            @keydown.escape.prevent="$modal.hide(`linkPrompt-${editorId}`)"
            @submit.prevent="$emit('submit')"
        >
            {{ $t("address") }}:
            <CharInputWrapping v-model="linkAttrs.href" />
            {{ $t("title") }}:
            <CharInputWrapping v-model="linkAttrs.title" />
            <div class="mt-4">
                <button
                    class="button is-blue"
                    type="submit"
                >
                    {{ $t("ok") }}
                </button>
                <button
                    class="button"
                    type="button"
                    @click="$modal.hide(`linkPrompt-${editorId}`)"
                >
                    {{ $t("cancel") }}
                </button>
            </div>
        </form>
    </div>
</Modal>
</template>

<script>
import $ from "jquery"
import CharInputWrapping from "@components/forms/widgets/CharInputWrapping"

export default {
    name: "RichTextLinkPrompt",
    components: {
        CharInputWrapping,
    },
    inject: ["editorId"],
    props: {
        linkAttrs: Object,
    },
    methods: {
        focus() {
            let input = this.$refs.form.elements[0]
            if (input) this.$nextTick(() => input.focus())
        },
    },
    mounted() {
        // Move the modal out of the menubar to fix z-index + position:sticky issues
        $(this.$el).appendTo("body")
    },
    beforeDestroy() {
        this.$modal.hide(`linkPrompt-${this.editorId}`)

        // Elements appended to body must be removed manually, because Vue.js won't do it automatically.
        if (this.$el) {
            this.$el.remove()
        }
    },
    i18n: {
        messages: {
            fr: {
                address: "Adresse",
            },
            en: {
                address: "Address",
            },
        },
    },
}
</script>
