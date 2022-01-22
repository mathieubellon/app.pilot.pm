<template>
<span
    v-if="label"
    class="Label"
    :style="style"
>
    <SmartLink
        v-if="goToListOnClick && listUrl"
        :style="style"
        :to="listUrl"
    >
        {{ label.name }}
    </SmartLink>
    <template v-else>
        <span :style="style">{{ label.name }}</span>
    </template>
</span>
</template>

<script>
import urls from "@js/urls"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "Label",
    mixins: [PilotMixin],
    props: {
        label: Object,
        // If true, a click on the label will redirect on the corresponding list, filtered by this label
        goToListOnClick: Boolean,
    },
    computed: {
        style() {
            if (this.label.background_color) {
                return { "background-color": this.label.background_color, color: this.label.color }
            } else {
                return { "background-color": this.label.color, color: "#000" }
            }
        },
        listUrl() {
            let baseUrl, queryParamName
            switch (this.label.target_type) {
                case "asset_folder":
                    baseUrl = urls.assetsApp
                    queryParamName = "folder"
                    break
                case "channel_type":
                    baseUrl = urls.channelsApp
                    queryParamName = "type"
                    break
                case "item_tags":
                    baseUrl = urls.itemsApp
                    queryParamName = "tags"
                    break
                case "project_category":
                    baseUrl = urls.projectsApp
                    queryParamName = "category"
                    break
                case "project_priority":
                    baseUrl = urls.projectsApp
                    queryParamName = "priority"
                    break
                case "project_tags":
                    baseUrl = urls.projectsApp
                    queryParamName = "tags"
                    break
            }
            if (!baseUrl || !queryParamName) return null
            return `${baseUrl}?${queryParamName}=${this.label.id}`
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.Label {
    @apply inline-flex items-center;
    @apply px-2 py-1;
    @apply transition ease-in-out duration-150;
    @apply border border-transparent;
    @apply rounded-md;

    @apply text-sm leading-5 font-medium;
    @apply text-gray-800 bg-gray-100;
    @apply cursor-pointer;
    @apply whitespace-no-wrap;
}
</style>
