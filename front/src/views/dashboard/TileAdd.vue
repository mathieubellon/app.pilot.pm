<template>
<div class="flex">
    <a
        class="button is-blue is-small"
        @click.prevent="openOffPanel('tilePicker')"
    >
        {{ $t("addATile") }}
    </a>
    <OffPanel name="tilePicker">
        <div slot="offPanelTitle">
            {{ $t("selectTileType") }}
        </div>

        <div slot="offPanelBody">
            <div class="tileList">
                <div class="offPanelTitle">{{ $t("staticTileTitle") }}</div>
                <div class="offPanelDescription">{{ $t("staticTileDescription") }}</div>

                <div
                    v-if="tile.isBuiltIn"
                    v-for="(tile, index) in tilesRemaining"
                    class="Tile"
                    :key="tile.name"
                >
                    <div class="TileTitle">{{ tile.title }}</div>
                    <div class="TileDescription">{{ tile.description }}</div>
                    <div
                        class="button small hollow"
                        @click.once="addTileToUserTiles(tile)"
                    >
                        {{ $t("clickToAdd") }}
                    </div>
                </div>
            </div>
            <div class="tileList">
                <div class="offPanelTitle">{{ $t("dynamicTileTitle") }}</div>
                <div class="offPanelDescription">{{ $t("dynamicTileDescription") }}</div>
                <Loading name="fetchSavedFilter" />

                <div
                    v-if="!tile.isBuiltIn"
                    v-for="(tile, index) in tilesRemaining"
                    class="Tile"
                    :key="tile.name"
                >
                    <div class="TileTitle">{{ tile.title }}</div>
                    <div class="TileDescription">{{ tile.description }}</div>
                    <div
                        class="button small hollow"
                        @click.once="addTileToUserTiles(tile)"
                    >
                        {{ $t("clickToAdd") }}
                    </div>
                </div>
            </div>
        </div>
    </OffPanel>
</div>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "TileAdd",
    mixins: [PilotMixin],
    computed: {
        ...mapState("savedFilter", ["savedFilters"]),
        ...mapGetters("dashboard", ["tilesRemaining"]),
    },
    methods: {
        ...mapActions("dashboard", ["addTileToUserTiles"]),
    },
    i18n: {
        messages: {
            fr: {
                addATile: "Ajouter un bloc info",
                clickToAdd: "Cliquez pour ajouter à votre tableau de bord",
                missingBox: "Un bloc vous manque ? Demandez le à support@pilot.pm",
                myItems: "Mes contenus",
                myProjects: "Mes projets",
                selectTileType: "Choisissez un bloc info",
                dynamicTileTitle: "Blocs dynamiques",
                dynamicTileDescription:
                    "Lorsque vous enregistrez un filtre de liste nous l'affichons ici pour que vous puissiez le mettre sur votre tableau de bord",
                staticTileTitle: "Blocs statiques",
                staticTileDescription:
                    "Les bloc d'infos statiques sont des blocs 'par défaut' présents pour tous les comptes.",
            },
            en: {
                addATile: "Add an info box",
                clickToAdd: "Click to add to your dashboard",
                missingBox: "A box is missing ? Ask for it at support@pilot.pm",
                myItems: "My items",
                myProjects: "My projects",
                selectTileType: "Select an info box",
                dynamicTileTitle: "Dynamic blocks",
                dynamicTileDescription:
                    "When you save a list filter we display it here so you can put it on your dashboard",
                staticTileTitle: "Static blocks",
                staticTileDescription:
                    "Static info blocks are 'default' blocks present for all accounts.",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
.AddTileDescription {
    margin-bottom: 1em;
    font-size: 1.1em;
}

.Tile {
    padding: 0.85em;
    margin-bottom: 0.5em;
    border-radius: 5px;
    border: 1px solid $gray-light;
    background-color: $gray-lighter;
    .button {
        margin: 1em 0 0 0;
        font-weight: bolder;
    }
}
.TileTitle {
    font-weight: bolder;
    margin-bottom: 0em;
}
.TileDescription {
    font-size: 0.9em;
}

.tileList {
    margin-bottom: 1em;
    margin-top: 3em;
}
.offPanelTitle {
    font-weight: bolder;
}
.offPanelDescription {
    color: $gray;
    margin-bottom: 1em;
}

.noDynamicTile {
    margin-left: 1em;
    font-style: italic;
}
.empty {
    box-shadow: None;
    margin-top: 1.6em;
}
.empty:hover {
    cursor: pointer;
    background-color: #fff;
    color: $blue;
    .AddTileDescription {
        display: inline;
    }
    a {
        text-decoration: none;
    }
}
</style>
