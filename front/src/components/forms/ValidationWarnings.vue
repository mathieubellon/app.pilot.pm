<template>
<div
    v-if="warnings"
    class="form__field__warning mr-1"
>
    <template v-if="!showOnlyWhenDirty || warnings.$dirty">
        <div v-if="warnings.maxLength === false">
            {{ $t("contentTooLong") }}
        </div>
        <div v-if="warnings.prosemirrorMaxLength === false">
            {{ $t("contentTooLong") }}
        </div>
    </template>
</div>
</template>

<script>
export default {
    name: "ValidationWarnings",
    props: {
        warnings: Object,
        showOnlyWhenDirty: {
            type: Boolean,
            default: true,
        },
    },
    i18n: {
        messages: {
            fr: {
                contentTooLong: "Contenu plus long que la taille conseillée",
            },
            en: {
                contentTooLong: "Content longer than the advised length",
            },
        },
    },
}
</script>
