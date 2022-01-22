<template>
<div class="WikiPage w-full overflow-y-auto flex justify-center">
    <div class="w-full max-w-4xl p-4">
        <Loadarium name="fetchWikiPage">
            <!-- Wiki page edition ( create/update ) -->
            <!-- DO NOT move the p-4 to the root element, it won't work with the sticky RichTextMenuBar -->
            <div
                v-if="wikiPageInEdition"
                class="bg-white rounded p-7 border border-gray-100"
            >
                <div class="font-extrabold text-2xl mb-4">
                    <template v-if="wikiPageInEdition.id">
                        {{ $t("updatingPage") }} {{ wikiPage.name }}
                    </template>
                    <template v-else>
                        {{ $t("newPage") }}
                    </template>
                </div>

                <FormField
                    :schema="{
                        type: 'char',
                        label: $t('title'),
                        placeholder: $t('title'),
                    }"
                    v-model.trim="wikiPageInEdition.name"
                    :vuelidate="$v.wikiPageInEdition.name"
                />

                <FormField
                    v-model="wikiPageInEdition.content"
                    :schema="{
                        type: 'richText',
                        label: $t('content'),
                        editorSchema: wikiSchema,
                    }"
                />
            </div>

            <!-- Wiki page display -->
            <div v-else>
                <div class="WikiBox rounded bg-white shadow">
                    <h2 class="font-extrabold text-3xl leading-tight">
                        {{ wikiPage.name }}
                    </h2>

                    <div
                        v-if="contentHtml"
                        class="text-lg mb-4"
                    >
                        <a href="#assets">
                            {{ $t("assets") }}
                        </a>
                        &bullet;
                        <a href="#comments">
                            {{ $t("comments") }}
                        </a>
                    </div>

                    <div
                        v-if="contentHtml"
                        v-html="contentHtml"
                        class="RichTextStyling text-lg"
                    />

                    <div
                        v-else
                        class="mt-4 mb-32 text-lg"
                    >
                        <div class="flex flex-col my-4">
                            <span class="italic">{{ $t("noContentYet") }}</span>
                            <AdminButton
                                aClass="button my-1 self-start"
                                @click="startWikiPageEdition"
                            >
                                {{ $t("addContent") }}
                            </AdminButton>
                        </div>
                    </div>
                </div>

                <div class="WikiBox border border-gray-200 rounded">
                    <h2
                        id="assets"
                        class="font-bold text-2xl"
                    >
                        {{ $t("linkedAssets") }}
                    </h2>

                    <LinkedAssets
                        class="w-full px-0"
                        :gridView="false"
                        namespace="wiki"
                        :showPlaceholder="false"
                    />
                </div>

                <div class="WikiBox border border-gray-200 rounded">
                    <h2
                        id="comments"
                        class="font-bold text-2xl"
                    >
                        {{ $t("comments") }}
                    </h2>

                    <ActivityFeed
                        class="w-full"
                        namespace="wiki"
                        :showActivites="false"
                    />
                </div>
            </div>
        </Loadarium>
    </div>
</div>
</template>

<script>
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { required } from "vuelidate/lib/validators"
import { wikiSchema } from "@richText/schema"
import { parseQueryString } from "@js/queryString"
import PilotMixin from "@components/PilotMixin"

import LinkedAssets from "@views/assets/linked/LinkedAssets.vue"
import ActivityFeed from "@views/activity/ActivityFeed.vue"
import AdminButton from "@components/admin/AdminButton"

export default {
    name: "WikiPage",
    mixins: [PilotMixin],
    components: {
        LinkedAssets,
        ActivityFeed,
        AdminButton,
    },
    data: () => ({
        wikiSchema,
    }),
    validations: {
        wikiPageInEdition: {
            name: { required },
        },
    },
    computed: {
        ...mapState("wiki", ["wikiPage", "wikiPageInEdition"]),
        contentHtml() {
            if (!this.wikiPage.content) {
                return ""
            }
            return wikiSchema.HTMLFromJSON(this.wikiPage.content)
        },
    },
    methods: {
        ...mapMutations("wiki/linkedAssets", ["initLinkedAssetsStore", "setLinkedAssets"]),
        ...mapMutations("wiki/activityFeed", ["initActivityFeedStore", "setActivities"]),
        ...mapMutations("wiki", ["setWikiPageInEdition", "setWikiPageInEditionValidation"]),
        ...mapActions("wiki/linkedAssets", ["fetchLinkedAssets"]),
        ...mapActions("wiki/activityFeed", ["fetchActivities"]),
        ...mapActions("wiki", ["fetchWikiPage", "startWikiPageEdition"]),
        init() {
            let queryParams = parseQueryString(document.location.search)
            let initialScrollTo = (queryParams.scrollto || [])[0]

            this.setWikiPageInEdition(null)
            this.setLinkedAssets([])
            this.setActivities([])

            this.$v.$reset()
            this.fetchWikiPage().then((wikiPage) => {
                this.initLinkedAssetsStore({
                    contentType: this.contentTypes.WikiPage,
                    objectId: wikiPage.id,
                })

                this.initActivityFeedStore({
                    contentType: this.contentTypes.WikiPage,
                    objectId: wikiPage.id,
                })

                this.fetchLinkedAssets()
                let activitiesPromise = this.fetchActivities()

                if (initialScrollTo && initialScrollTo.startsWith("comment")) {
                    activitiesPromise.then(() => {
                        let $commentActivity = $("." + initialScrollTo)
                        if (!$commentActivity.length) {
                            return
                        }
                        $(".WikiPage").scrollTop($commentActivity.offset().top)
                        // Make the comment box blink
                        $commentActivity.addClass("twinkle")
                    })
                }
            })
        },
    },
    created() {
        this.setWikiPageInEditionValidation(this.$v)
    },
    beforeRouteEnter(to, from, next) {
        next((vm) => vm.init())
    },
    beforeRouteUpdate(to, from, next) {
        if (to.params.id != from.params.id) {
            this.$nextTick(this.init)
        }
        next()
    },
    i18n: {
        messages: {
            fr: {
                addContent: "Cliquez ici pour commencer à rédiger.",
                updatingPage: "Modification de la page",
                newPage: "Nouvelle page",
                noContentYet: "Cette page de wiki n'a pas encore de contenu.",
            },
            en: {
                addContent: "Click here to start writing.",
                updatingPage: "Changing the page",
                newPage: "New page",
                noContentYet: "This wiki page has no content yet.",
            },
        },
    },
}
</script>

<style lang="scss">
.WikiBox {
    @apply px-8 py-4 mb-10;
}
</style>
