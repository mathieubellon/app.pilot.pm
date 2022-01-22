<template>
<div>
    <div class="p-5 mb-4 bg-gray-50 border-l-2 border-blue-500 text-gray-700">
        <div class="font-bold">{{ $t("information") }}</div>
        <div>{{ $t("clickToManage") }}</div>
    </div>

    <div
        v-for="targetTypeSpec in targetTypeSpecs"
        class="LabelTargetTypeList__listElement"
        :key="targetTypeSpec.name"
        @click="$router.push({ name: 'labelsList', params: { targetType: targetTypeSpec.name } })"
    >
        <div class="flex w-80">
            <div class="font-bold w-40">{{ targetTypeSpec.model }}</div>
            :
            <div class="ml-2 text-normal">{{ targetTypeSpec.fieldNamePlural }}</div>
        </div>
        <div class="button">{{ $t("edit") }}</div>
    </div>
</div>
</template>

<script>
import FullLayout from "@components/layout/FullLayout"

export default {
    name: "LabelTargetTypeList",
    components: {
        FullLayout,
    },
    computed: {
        targetTypeSpecs() {
            return this.$store.state.labels.targetTypeSpecs
        },
    },
    i18n: {
        messages: {
            fr: {
                clickToManage:
                    "Les labels sont des \"étiquettes\" servant à ajouter de l'information à un objet (contenu, projet, canal etc ..). Leur administration est complètement libre pour vous permettre d'organiser, classer, trier ces objets",
            },
            en: {
                clickToManage:
                    "Labels add information to an object (content, project, channel etc...). Their administration is completely free to allow you to organize, classify, sort these objects",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.LabelTargetTypeList__listElement {
    @apply flex justify-between items-center bg-white p-4 w-full mb-2 border border-gray-100 rounded;
    cursor: pointer;

    &:hover {
        @apply bg-gray-100 border-gray-200;
    }
}
</style>
