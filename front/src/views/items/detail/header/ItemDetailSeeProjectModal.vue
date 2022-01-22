<template>
<Modal
    name="itemDetailSeeProject"
    :adaptive="true"
    :height="modalHeight"
    :max-width="700"
    :pivotY="0.2"
    width="95%"
>
    <div
        v-if="item.project"
        class="p-6 h-full w-full overflow-y-auto"
    >
        <SmartLink
            class="text-xl font-bold flex items-center"
            :to="item.project.url"
        >
            <Icon
                class="mr-1"
                name="Project"
                size="20px"
            />
            {{ item.project.name }}
        </SmartLink>

        <div class="mt-1 mb-2 w-full">
            <div class="text-sm font-semibold text-gray-900">
                {{ $t("description") }}
            </div>

            <div
                v-if="projectDescriptionHtml"
                class="border bg-gray-50 p-1 cursor-pointer"
                @click="showProjectDetails = !showProjectDetails"
            >
                <div class="float-right ml-2">
                    <Icon
                        class="text-blue-400"
                        :name="showProjectDetails ? 'ChevronUp' : 'ChevronDown'"
                    />
                </div>

                <div
                    v-html="projectDescriptionHtml"
                    class="text-gray-700"
                    :class="{
                        'h-6 overflow-hidden': !showProjectDetails,
                        RichTextStyling: showProjectDetails,
                    }"
                />
            </div>

            <span v-else>{{ $t("noDescription") }}</span>
        </div>

        <div
            v-if="item.project.items"
            class="flex flex-col flex-start"
        >
            <div class="text-sm font-semibold text-gray-900">{{ $t("itemsInProject") }}</div>
            <button
                v-for="projectItem in item.project.items"
                class="button mb-1 self-start"
                type="button"
            >
                <SmartLink :to="projectItem.url">
                    {{ projectItem.title | defaultVal("N/A") }}
                </SmartLink>
                <!--<br />-->
                <!--#{{ projectItem.id }} |-->
                <!--<template v-if="projectItem.language">{{ projectItem.language }} |</template>-->
                <!--{{ projectItem.updated_at | dateTimeFormat }}-->
            </button>
        </div>
    </div>
</Modal>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { richTextSchema } from "@richText/schema"
import PilotMixin from "@components/PilotMixin"
import ResponsiveMixin from "@components/ResponsiveMixin"

export default {
    name: "ItemDetailSeeProjectModal",
    mixins: [PilotMixin, ResponsiveMixin],
    data: () => ({
        showProjectDetails: false,
    }),
    computed: {
        ...mapState("itemDetail", ["item"]),
        modalHeight() {
            return this.viewportLTETablet ? "90%" : "50%"
        },
        projectDescriptionHtml() {
            return richTextSchema.HTMLFromJSON(this.item.project.description)
        },
    },
    i18n: {
        messages: {
            fr: {
                itemsInProject: "Contenus dans le projet",
            },
            en: {
                itemsInProject: "Contents in project",
            },
        },
    },
}
</script>

<style lang="scss"></style>
