<template>
<Popper
    closeOnClickSelector=".willClose"
    triggerElementName="PopperRef"
    triggerType="click"
    @show="init"
>
    <template #triggerElement>
        <a
            class="button is-topbar"
            ref="PopperRef"
        >
            {{ $t("filterActions") }}
            <!-- The empty span is required to correctly align with flex display -->
            <Icon
                class="caret"
                name="ChevronDown"
            />
        </a>
    </template>

    <template #content>
        <div class="max-w-sm">
            <div class="menu-title">{{ selectedSavedFilter.name }}</div>

            <button
                class="menu-item is-teal willClose"
                @click="$modal.show(`sharings-${selectedSavedFilter.type}`)"
            >
                <Icon name="Share" />
                <div class="flex flex-col items-start">
                    <span>{{ $t("publicShareFilter") }}</span>
                    <span class="menu-item-description">
                        {{ $t("publicShareFilterDescription") }}
                    </span>
                </div>
            </button>

            <button
                class="menu-item willClose"
                @click="openOffPanel('SavedFilterInternalSharePanel')"
            >
                <Icon name="Share" />
                <div class="flex flex-col items-start">
                    <span>{{ $t("internalShareFilter") }}</span>
                    <span class="menu-item-description">
                        {{ $t("internalShareFilterDescription") }}
                    </span>
                </div>
            </button>

            <button
                class="menu-item willClose"
                @click="openOffPanel('savedFilterCreateUpdate')"
            >
                <Icon name="Edit" />
                {{ $t("editFilterSettings") }}
            </button>

            <Loadarium name="fetchNotificationFeeds">
                <button
                    v-if="existingNotificationFeed || createdNotificationFeed"
                    class="menu-item willClose"
                    @click="goToNotificationSettings"
                >
                    <Icon name="Bell" />
                    <div class="flex flex-col items-start">
                        <span>
                            {{ $t(existingNotificationFeed ? "feedAlreadyExists" : "feedCreated") }}
                        </span>
                        <span class="menu-item-description">
                            {{ $t("goToNotificationSettings") }}
                        </span>
                    </div>
                </button>

                <button
                    v-else
                    class="menu-item"
                    @click="createNotificationFeed"
                >
                    <Icon name="Bell" />
                    <Loadarium name="createFeedForSavedFilter">
                        <div class="flex flex-col items-start">
                            <span>{{ $t("monitorFilter") }}</span>
                            <span class="menu-item-description">
                                {{ $t("monitorFilterDescription") }}
                            </span>
                        </div>
                    </Loadarium>
                </button>
            </Loadarium>

            <div
                v-if="exportStarted"
                class="menu-item cursor-default hover:bg-transparent"
            >
                <Icon name="Export" />
                <div class="flex flex-col items-start">
                    <span>✓ {{ $t("exportStarted") }}</span>
                    <span class="menu-item-description">
                        {{ $t("youWillBeNotifiedAfterExport") }}
                    </span>
                </div>
            </div>
            <button
                v-else
                class="menu-item"
                @click="exportFilter"
            >
                <Icon name="Export" />
                <Loadarium name="exportFilter">
                    <div class="flex flex-col items-start">
                        <span>{{ $t("exportFilter") }}</span>
                        <span class="menu-item-description">
                            {{ $t("youWillBeNotifiedAfterExport") }}
                        </span>
                    </div>
                </Loadarium>
            </button>

            <button
                class="menu-item is-red willClose"
                @click="openOffPanel('savedFilterDelete')"
            >
                <Icon name="Trash" />
                {{ $t("deleteFilter") }}
            </button>
        </div>
    </template>
</Popper>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import urls from "@js/urls.js"
import { $httpX } from "@js/ajax.js"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "SavedFilterActions",
    mixins: [PilotMixin],
    data: () => ({
        createdNotificationFeed: null,
        existingNotificationFeed: null,
        exportStarted: false,
    }),
    computed: {
        ...mapGetters("savedFilter", ["selectedSavedFilter"]),
        ...mapGetters("notificationSettings", ["getExistingNotificationFeed"]),
    },
    methods: {
        ...mapActions("notificationSettings", [
            "fetchNotificationFeeds",
            "createFeedForSavedFilter",
            "blinkNotificationFeed",
        ]),
        init() {
            this.createdNotificationFeed = null
            this.existingNotificationFeed = this.getExistingNotificationFeed(
                this.selectedSavedFilter,
            )
        },
        createNotificationFeed() {
            this.createFeedForSavedFilter(this.selectedSavedFilter).then((savedFilter) => {
                this.createdNotificationFeed = savedFilter
            })
        },
        goToNotificationSettings() {
            this.blinkNotificationFeed(this.getExistingNotificationFeed(this.selectedSavedFilter))
            this.openOffPanel("NotificationsSettingsPanel")
        },
        exportFilter() {
            $httpX({
                name: "exportFilter",
                method: "PUT",
                url: urls.savedFiltersExport.format({ id: this.selectedSavedFilter.id }),
                commit: this.$store.commit,
            }).then(() => (this.exportStarted = true))
        },
    },
    created() {
        this.fetchNotificationFeeds().then(() => {
            this.init()
        })
    },
    i18n: {
        messages: {
            fr: {
                deleteFilter: "Supprimer définitivement",
                editFilterSettings: "Modifier les paramètres du filtre",
                exportFilter: "Exporter ce filtre (.xlsx)",
                feedCreated: "Alerte créée",
                feedAlreadyExists: "Une alerte existe déjà pour ce filtre",
                filterActions: "Actions filtre",
                goToNotificationSettings: "Cliquez ici pour gérer vos notifications",
                internalShareFilter: "Partager ce filtre (interne)",
                internalShareFilterDescription:
                    "Donner accès à ce filtre à d'autre utilisateurs de ce desk",
                monitorFilter: "Recevoir des notifications",
                monitorFilterDescription:
                    "Recevez une notification quand un contenu de ce filtre est ajouté, modifié ou retiré",
                Actions: "Actions",
                publicShareFilter: "Partager ce filtre (externe)",
                publicShareFilterDescription:
                    "Création d'un lien public et unique à partager avec vos contacts externes",
            },
            en: {
                deleteFilter: "Delete permanently",
                editFilterSettings: "Modify filter settings",
                exportFilter: "Export this filter (.xlsx)",
                feedAlreadyExists: "You already watch this filter",
                feedCreated: "You now watch this filter",
                filterActions: "Filter actions",
                goToNotificationSettings: "Click here to manage your notifications",
                internalShareFilter: "Share this filter (internal)",
                internalShareFilterDescription:
                    "Give access to this filter to other users in this desk",
                monitorFilter: "Receive notifications",
                monitorFilterDescription:
                    "Receive a notification when a content of this filter is added, modified or removed",
                Actions: "Actions",
                publicShareFilter: "Share this filter (external)",
                publicShareFilterDescription:
                    "Creating a unique and public link to share with your external contacts",
            },
        },
    },
}
</script>
