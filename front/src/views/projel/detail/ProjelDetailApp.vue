<template>
<MainLayout :appBodyScroll="!isHierarchyView">
    <template #title>
        <ProjelDetailTopbar v-if="projel.id" />
        <!-- Initial Projel Loading -->
        <span v-else>{{ $t("loading") }}</span>
    </template>

    <template #actions>
        <ProjelDetailTopBarActions v-if="projel.id" />
    </template>

    <template #middlebar>
        <ProjelDetailTabs v-if="projel.id" />
    </template>

    <template #content>
        <ProjelIdeaStateBar />
        <div
            :class="{
                'p-0': isHierarchyView,
                'p-2 md:p-8': !isHierarchyView,
            }"
        >
            <router-view />
        </div>

        <SharingsModal
            v-if="isChannelRoute"
            :sharingTarget="{
                type: 'channel',
                channel_id: projelId,
            }"
        />

        <SharingsModal
            v-if="isProjectRoute"
            :sharingTarget="{
                type: 'project',
                project_id: projelId,
            }"
        />

        <ItemAddPanel
            v-if="isChannelRoute"
            :initialChannel="projel"
        />
        <ItemAddPanel
            v-if="isProjectRoute"
            :initialProject="projel"
        />

        <ProjectCopyOffpanel />
    </template>
</MainLayout>
</template>

<script>
import $ from "jquery"
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import { parseQueryString } from "@js/queryString"
import PilotMixin from "@components/PilotMixin"
import MainLayout from "@components/layout/MainLayout"
import ProjelDetailTopbar from "./ProjelDetailTopbar"
import ProjelIdeaStateBar from "./ProjelIdeaStateBar"
import ProjelDetailTabs from "./ProjelDetailTabs"
import SharingsModal from "@views/sharings/internal/SharingsModal"
import ProjelDetailTopBarActions from "./ProjelDetailTopBarActions"
import ProjectCopyOffpanel from "./ProjectCopyOffpanel"
import ItemAddPanel from "@views/items/ItemAddPanel.vue"

export default {
    name: "ProjelDetailApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
        ProjelDetailTopbar,
        ProjelDetailTabs,
        ProjelIdeaStateBar,
        SharingsModal,
        ProjelDetailTopBarActions,
        ProjectCopyOffpanel,
        ItemAddPanel,
    },
    computed: {
        ...mapState("projelDetail", ["projel", "fieldsCurrentlyUpdating"]),
        ...mapGetters("projelDetail", [
            "projelId",
            "projelContentType",
            "isChannelRoute",
            "isProjectRoute",
        ]),
        isHierarchyView() {
            return (
                this.currentRouteName == "projectDetail-hierarchy" ||
                this.currentRouteName == "channelDetail-hierarchy"
            )
        },
    },
    methods: {
        ...mapMutations("projelDetail/activityFeed", ["initActivityFeedStore"]),
        ...mapMutations("projelDetail/linkedTasks", ["initLinkedTasksStore"]),
        ...mapMutations("projelDetail/linkedAssets", ["initLinkedAssetsStore"]),
        ...mapActions("projelDetail/activityFeed", ["fetchActivities"]),
        ...mapActions("projelDetail", ["fetchProjel"]),
    },
    created() {
        let projelPromise = this.fetchProjel({ resetBeforeFetch: true })

        this.initActivityFeedStore({
            contentType: this.projelContentType,
            objectId: this.projelId,
        })
        let activitiesPromise = this.fetchActivities()

        this.initLinkedTasksStore({
            contentType: this.projelContentType,
            objectId: this.projelId,
        })

        this.initLinkedAssetsStore({
            contentType: this.projelContentType,
            objectId: this.projelId,
        })

        let queryParams = parseQueryString(document.location.search)
        let initialScrollTo = (queryParams.scrollto || [])[0]
        let showTaskId = (queryParams.showTask || [])[0]

        // An initial comment should be shown
        if (initialScrollTo && initialScrollTo.startsWith("comment")) {
            let routeName = this.isChannelRoute
                ? "channelDetail-activity"
                : "projectDetail-activity"
            // Show the activity/comment tab
            this.$router.replace({ name: routeName, query: queryParams })

            activitiesPromise.then(() => {
                let $commentActivity = $("." + initialScrollTo)
                if (!$commentActivity.length) {
                    return
                }
                $("#app-body").scrollTop($commentActivity.offset().top)
                // Make the comment box blink
                $commentActivity.addClass("twinkle")
            })
        }

        // An initial task should be shown
        if (showTaskId) {
            // Show the task tab
            let routeName = this.isChannelRoute ? "channelDetail-tasks" : "projectDetail-tasks"
            this.$router.replace({ name: routeName, query: queryParams })

            projelPromise.then(() => {
                let $taskElement = $("#LinkedTask-" + showTaskId)
                if (!$taskElement.length) {
                    return
                }
                $("#app-body").scrollTop($taskElement.offset().top)
                // Make the task element box blink
                $taskElement.addClass("twinkle")
            })
        }
    },
}
</script>
