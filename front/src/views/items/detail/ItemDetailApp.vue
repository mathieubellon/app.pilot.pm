<template>
<MainLayout
    class="ItemDetailApp"
    :appBodyScroll="false"
    :headerClass="headerClass"
>
    <template #title>
        <ItemDetailTopBarTitle v-if="item.id" />

        <!-- Initial Item Loading -->
        <template v-else>
            {{ $t("loadingContent") }}
        </template>
    </template>

    <template #subtitle>
        <ItemDetailTopBarSubtitle v-if="item.id && !item.in_trash" />
    </template>

    <template #actions>
        <ItemDetailTopBarActions v-if="item.id" />
    </template>

    <template #middlebar>
        <div class="flex flex-col w-full">
            <ItemMiddleBar
                v-if="item.id && !item.in_trash"
                :class="headerClass"
            />

            <div
                v-if="isSavingStale"
                class="py-8 px-4 bg-red-700 text-red-100 text-lg"
            >
                <Icon name="Frown" />
                Un problème technique majeur a été détecté. Vos modifications ne sont plus sauvegardées
                correctement.
                <Icon name="Frown" />
                <br />
                <span
                    v-if="lastSuccessfulSaveMoment"
                    class="font-bold text-md"
                >
                    La dernière sauvegarde a été effectuée
                    {{ lastSuccessfulSaveMoment.fromNow() }}
                    ( {{ lastSuccessfulSaveMoment | dateFormat("HH:mm:ss") }} )
                </span>
                <br />
                <span class="text-yellow-200 font-bold text-xl">
                    Nous conseillons de copier vos données avant de quitter ou recharger cette page.
                </span>
            </div>
            <ItemSavingRecoveryBar />
            <ItemFrozenBar :item="item" />
        </div>
    </template>

    <template
        v-if="item.id"
        #content
    >
        <ItemAddPanel :copiedFrom="copiedFrom" />

        <ItemDetailBody />

        <SharingsModal
            :sharingTarget="{
                type: 'item',
                item_id: itemId,
            }"
        />
        <ItemFreezeModal />
        <ItemDetailSeeProjectModal />
    </template>
</MainLayout>
</template>

<script>
import $ from "jquery"
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import moment from "moment"
import { waitUntil } from "@js/utils"
import { parseQueryString } from "@js/queryString"
import { LocalStorageWrapper } from "@js/localStorage.js"
import realtime from "@js/realtime"
import { REALTIME_STATES } from "@/store/modules/ItemContentFormStore.js"
import { ItemPositioner } from "@js/items/itemsUtils"
import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"
import ItemDetailTopBarActions from "./header/ItemDetailTopBarActions"
import ItemDetailTopBarTitle from "./header/ItemDetailTopBarTitle"
import ItemDetailTopBarSubtitle from "./header/ItemDetailTopBarSubtitle"
import ItemMiddleBar from "./header/ItemMiddleBar"
import ItemDetailBody from "./ItemDetailBody"
import ItemAddPanel from "../ItemAddPanel.vue"

import ItemSavingRecoveryBar from "./ItemSavingRecoveryBar.vue"
import ItemFrozenBar from "./ItemFrozenBar.vue"
import ItemFreezeModal from "./ItemFreezeModal.vue"
import ItemDetailSeeProjectModal from "./header/ItemDetailSeeProjectModal.vue"
import AssetList from "@views/assets/list/AssetList.vue"
import SharingsModal from "@views/sharings/internal/SharingsModal"

// Time before saving is considered stale ( 30 seconds )
const STALE_SAVING_DELAY = 30000
// Interval for checking if the saving is stale ( 5 seconds )
const STALE_SAVING_CHECK_INTERVAL = 5000

let localOpenedDrawer = new LocalStorageWrapper("ItemDetailApp.openedDrawer")
let staleSavingIntervalId = null

export default {
    name: "ItemDetailApp",
    mixins: [PilotMixin],
    components: {
        AssetList,
        ItemAddPanel,
        ItemDetailBody,
        ItemDetailSeeProjectModal,
        ItemDetailTopBarActions,
        ItemFreezeModal,
        ItemFrozenBar,
        ItemMiddleBar,
        ItemSavingRecoveryBar,
        ItemDetailTopBarSubtitle,
        ItemDetailTopBarTitle,
        MainLayout,
        SharingsModal,
    },
    data: () => ({
        isSavingStale: false,

        REALTIME_STATES,
        moment,
    }),
    computed: {
        ...mapState("itemDetail", ["item", "openedDrawer"]),
        ...mapState("itemContentForm", [
            "annotationManagers",
            "desynchronized",
            "isDisconnectedAfterInactivity",
            "validation",
            "unconfirmedChangeMoment",
            "lastSuccessfulSaveMoment",
        ]),
        ...mapGetters("itemDetail", ["itemId", "findEditSession"]),
        ...mapGetters("itemContentForm", [
            "areAnnotationManagersReady",
            "anyPendingChanges",
            "anyUnconfirmedChanges",
            "currentRealtimeState",
        ]),
        copiedFrom() {
            return _.defaults({}, _.omit(this.item, ["id"]), { copied_from: this.item.id })
        },
        isFormInvalid() {
            return this.validation ? this.validation.$invalid : false
        },
        headerClass() {
            if (this.item.in_trash) {
                return "bg-yellow-50"
            } else if (this.currentRealtimeState == REALTIME_STATES.conflict) {
                return "bg-purple-100"
            }
            /*
            else if( this.isFormInvalid ){
                return 'bg-red-50'
            }
            */
        },
        isSaving() {
            return (
                (this.anyPendingChanges || this.anyUnconfirmedChanges) &&
                !(this.desynchronized || this.isDisconnectedAfterInactivity)
            )
        },
    },
    methods: {
        ...mapMutations("itemDetail/linkedAssets", ["initLinkedAssetsStore"]),
        ...mapMutations("itemDetail/linkedTasks", ["initLinkedTasksStore"]),
        ...mapMutations("itemDetail/activityFeed", ["initActivityFeedStore"]),
        ...mapActions("itemDetail/activityFeed", ["fetchActivities"]),
        ...mapActions("itemDetail", ["closePanel"]),
        ...mapActions("itemDetail", [
            "fetchItem",
            "fetchEditSessions",
            "showEditSession",
            "alignDecorationBoxes",
            "openDrawer",
        ]),
        ...mapActions("itemContentForm", ["initRealtime"]),
        init() {
            let queryParams = parseQueryString(document.location.search)
            let initialScrollTo = (queryParams.scrollto || [])[0]
            let diffWithVersion = (queryParams.showDiff || [])[0]
            let showTaskId = (queryParams.showTask || [])[0]
            let savedRightOpenPanel = localOpenedDrawer.get()

            let sessionFetchPromise = this.fetchEditSessions()

            this.fetchItem().then(() => {
                if (this.item.user_has_access) {
                    this.closePanel()

                    // Scroll to annotation if requested
                    if (initialScrollTo && initialScrollTo.startsWith("annotation")) {
                        let annotationId = initialScrollTo.split("-")[1]

                        // Wait for the annotation Manager to be ready before scrolling
                        waitUntil(
                            () => this.areAnnotationManagersReady,
                            () => {
                                for (let fieldName in this.annotationManagers) {
                                    let annotationManager = this.annotationManagers[fieldName]
                                    if (annotationId in annotationManager.annotations) {
                                        annotationManager.scrollToAnnotation(
                                            this.item.annotations[fieldName][annotationId],
                                        )
                                        break
                                    }
                                }
                            },
                            10000,
                        )
                    }

                    if (initialScrollTo && initialScrollTo.startsWith("comment")) {
                        this.openDrawer("activity")

                        // Wait for the panel to open and the activities to load
                        setTimeout(() => {
                            let $activityPanel = $(".ActivityFeed__ActivityList")
                            let $commentActivity = $("." + initialScrollTo)
                            if (!$activityPanel || !$commentActivity.length) {
                                return
                            }
                            $activityPanel.scrollTop(
                                $commentActivity.offset().top - $activityPanel.offset().top,
                            )
                            // Make the comment box blink
                            $commentActivity.addClass("twinkle")
                        }, 1000)
                    }

                    // An initial diff for a session id should be shown
                    if (diffWithVersion) {
                        this.openDrawer("history")
                        sessionFetchPromise.then(() => {
                            this.showEditSession({
                                editSession: this.findEditSession(diffWithVersion),
                                withDiff: true,
                            })
                        })
                    }

                    // An initial task should be shown
                    if (showTaskId) {
                        this.openDrawer("tasks")
                        // Wait for the panel to open
                        setTimeout(() => {
                            let $taskElement = $("#LinkedTask-" + showTaskId)
                            let $taskPanel = $(".LinkedTasks").parent()
                            $taskPanel.scrollTop(
                                $taskElement.offset().top - $taskPanel.offset().top,
                            )
                            // Make the task element blink
                            $taskElement.addClass("twinkle")
                        }, 300)
                    }

                    // Don't apply savedRightOpenPanel if a preceding init has already opened one
                    if (!this.openedDrawer && savedRightOpenPanel) {
                        this.openDrawer(savedRightOpenPanel)
                    }
                }
            })

            this.initRealtime({
                itemId: this.itemId,
                realtimeUser: _.pick(window.pilot.user, "id", "username", "avatar"),
            })

            this.initLinkedAssetsStore({
                contentType: this.contentTypes.Item,
                objectId: this.itemId,
            })
            this.initLinkedTasksStore({
                contentType: this.contentTypes.Item,
                objectId: this.itemId,
            })
            this.initActivityFeedStore({
                contentType: this.contentTypes.Item,
                objectId: this.itemId,
            })
            this.fetchActivities()

            // Init the decoration box alignment hacks

            // Align decoration boxes viewport movements
            this.itemPositioner = new ItemPositioner("DecorationBoxes", () =>
                this.alignDecorationBoxes(),
            )
            // Override the redraw callback for scrolling, because we don't need to do anything in this case
            this.itemPositioner.callbacks.onScroll = () => {}
            this.alignDecorationBoxes()

            /***********************
             * Leave page with unsaved change
             ************************/
            // If there's pending changes when the page unload,
            // display an alert box preventing the user to leave page without confirmation
            this.onBeforeUnload = () => {
                if (this.isSaving) {
                    return this.$t("leaveWithoutSaving")
                }
            }
            $(window).on("beforeunload", this.onBeforeUnload)

            /***********************
             * Stale saving detection
             ************************/
            staleSavingIntervalId = setInterval(() => {
                if (
                    this.unconfirmedChangeMoment &&
                    moment() - this.unconfirmedChangeMoment > STALE_SAVING_DELAY
                ) {
                    this.isSavingStale = true
                }
            }, STALE_SAVING_CHECK_INTERVAL)
        },
        terminate() {
            if (this.onBeforeUnload) {
                $(window).off("beforeunload", this.onBeforeUnload)
            }

            if (this.itemPositioner) {
                this.itemPositioner.detachEventHandlers()
            }

            if (staleSavingIntervalId) {
                clearInterval(staleSavingIntervalId)
            }

            this.$store.commit("itemDetail/reset")
            this.$store.commit("itemContentForm/reset")
        },
        askConfirmationIfIsSaving(ifConfirmed) {
            if (this.isSaving) {
                if (window.confirm(this.$t("leaveWithoutSaving"))) {
                    ifConfirmed()
                }
            } else {
                ifConfirmed()
            }
        },
    },
    watch: {
        openedDrawer() {
            localOpenedDrawer.set(this.openedDrawer)
        },
    },
    created() {
        this.init()
    },
    beforeDestroy() {
        this.terminate()
    },
    beforeRouteUpdate(to, from, next) {
        this.askConfirmationIfIsSaving(() => {
            // Disconnect from the realtime server
            realtime.disconnect()

            this.terminate()

            // We're going to another item
            if (to.params.id && to.params.id != from.params.id) {
                // Init the new Item from the API, and reconnect to the realtime server
                this.$nextTick(this.init)
            }
            next()
        })
    },
    beforeRouteLeave(to, from, next) {
        this.askConfirmationIfIsSaving(() => {
            // Disconnect from the realtime server
            realtime.disconnect()
            next()
        })
    },
    i18n: {
        messages: {
            fr: {
                leaveWithoutSaving:
                    "Vos modifications n'ont pas encore été sauvegardées, elles seront perdues si vous quittez cette page maintenant.",
                loadingContent: "Chargement du contenu..",
            },
            en: {
                leaveWithoutSaving:
                    "Your modifications have not been saved yet, they will be lost if you leave now.",
                loadingContent: "Loading content ..",
            },
        },
    },
}
</script>

<style>
.ItemDetailApp {
    #app-middlebar {
        position: sticky;
        top: 0;
        z-index: 30;
    }
    header {
        z-index: 40;
    }
}
</style>
