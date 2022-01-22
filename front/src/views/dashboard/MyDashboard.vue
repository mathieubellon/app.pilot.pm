<template>
<MainLayout class="DashboardApp">
    <template #title>
        {{ $t("dashboard") }}
    </template>

    <template #actions>
        <TileAdd />
    </template>

    <div
        class="p-2 md:p-8 md:pr-4 max-w-6xl"
        slot="content"
    >
        <div
            class="bg-purple-100 p-5 rounded border border-purple-300 mb-10 text-base text-purple-800 font-medium flex items-center"
        >
            <Icon
                class="mr-3 text-purple-500"
                name="Info"
            />
            {{ $t("wikiNewLocation") }}
            <router-link
                class="ml-1 underline font-bold"
                to="wiki"
            >
                {{ $t("wiki") }}
            </router-link>
        </div>
        <div
            v-if="displayFirstCreationItem || displayFirstCreationProject"
            class="MyDashboard__firstCreation container mb-8"
        >
            <SmartLink
                v-if="displayFirstCreationItem"
                class="button large is-blue"
                :to="urls.itemsApp.url"
            >
                {{ $t("createFirstItem") }}
            </SmartLink>
            <SmartLink
                v-if="displayFirstCreationProject"
                class="button large is-blue"
                :to="urls.projectsApp.url"
            >
                {{ $t("createFirstProject") }}
            </SmartLink>
        </div>

        <div class="flex flex-col justify-between">
            <Loadarium name="fetchSavedFilters">
                <div class="text-xl font-semibold mb-5">
                    {{ $t("infoBoxes") }}
                </div>

                <div
                    v-if="currentTiles.length == 0"
                    class="help-text"
                >
                    <div class="help-text-title">
                        <Icon
                            class="help-text-icon"
                            name="Dashboard"
                        />
                        <span>{{ $t("youHaveNoTilesHeader") }}</span>
                    </div>
                    <div class="help-text-content">{{ $t("youHaveNoTilesDescription") }}</div>
                    <button
                        class="button is-blue"
                        @click.prevent="openOffPanel('tilePicker')"
                    >
                        {{ $t("addInfoBox") }}
                    </button>
                </div>
            </Loadarium>
            <component
                v-for="(tile, index) in currentTiles"
                :is="tile.type"
                :key="tile.name"
                :tile="tile"
                :tileIndex="index"
            />
        </div>
    </div>
</MainLayout>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

import TileProjectList from "./TileProjectList.vue"
import TileItemList from "./TileItemList.vue"
import TileAdd from "./TileAdd.vue"
import TileActivityFeed from "./TileActivityFeed"

import MainLayout from "@components/layout/MainLayout"

export default {
    name: "MyDashboard",
    mixins: [PilotMixin],
    components: {
        TileAdd,
        TileActivityFeed,
        TileProjectList,
        TileItemList,
        MainLayout,
    },
    computed: {
        ...mapState("users", ["me"]),
        ...mapGetters("dashboard", ["currentTiles"]),
        displayFirstCreationItem() {
            return (
                !this.currentDesk.hasItems &&
                !this.currentDesk.hasProjects &&
                window.pilot.user.firstLogin
            )
        },
        displayFirstCreationProject() {
            return (
                !this.currentDesk.hasProjects &&
                !this.currentDesk.hasItems &&
                window.pilot.user.firstLogin
            )
        },
    },
    methods: {
        ...mapActions("savedFilter", ["fetchSavedFilters"]),
    },
    created() {
        this.fetchSavedFilters()
    },
    i18n: {
        messages: {
            fr: {
                addInfoBox: "Ajouter un bloc info",
                createFirstItem: "Créez le premier contenu",
                createFirstProject: "Créez le premier projet",
                infoBoxes: "Blocs d'informations",
                youHaveNoTilesDescription:
                    "Un bloc info est une liste de contenus ou de projets que vous souhaitez surveiller ..",
                youHaveNoTilesHeader: "Vous n'avez pas de bloc info.",
                wikiNewLocation: "Les documents de référence sont désormais présents dans le",
            },
            en: {
                addInfoBox: "Add an info box",
                createFirstItem: "Create the first content",
                createFirstProject: "Create the first project",
                infoBoxes: "Informations boxes",
                youHaveNoTilesDescription:
                    "An info box is a list of contents or projects that you would like to monitor ..",
                youHaveNoTilesHeader: "You have no info box",
                wikiNewLocation: "The reference documents are now present in the",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
@import "~@sass/include_media.scss";

.MyDashboard__headsUp {
    @apply flex flex-grow bg-white p-5 border rounded border-gray-200  w-1/3;
    @include media("<=tablet") {
        @apply mr-0 mb-2;
    }
}

.MyDashboard__headsUp__container {
    display: flex;
    flex-direction: row;
    min-height: 30px;
    padding-bottom: 2em;
}

.MyDashboard__headsUp__icon {
    @apply flex p-3 mr-3 items-center;
}
</style>
