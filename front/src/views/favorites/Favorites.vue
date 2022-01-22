<template>
<MainLayout>
    <template slot="title">
        {{ $t("myFavorites") }}
    </template>
    <div
        class="p-2 md:p-8 md:pr-4"
        slot="content"
    >
        <Loadarium name="fetchInitialData">
            <div
                v-if="favorites.length == 0"
                class="FavoritesPanelElement__EmptyState"
            >
                ⭐
                <div v-html="$t('NoFavorites')"></div>
            </div>

            <template v-else>
                <VueFuse
                    class="mb-4"
                    :defaultAll="true"
                    :keys="['target_name']"
                    :list="sortedFavorites"
                    :placeholder="$t('typeToFilter')"
                    :threshold="0.1"
                    @result="onFuseResult"
                />

                <template v-for="favorite in filteredFavorites">
                    <Deletarium
                        :confirmDeletionMessage="$t('confirmRemoveFavorite')"
                        :key="favorite.id"
                        loadingName="toggleFavorite"
                        @delete="deleteFavorite(favorite)"
                    >
                        <div
                            class="FavoritesPanelElement"
                            slot="notRequested"
                            slot-scope="{ requestDeletion }"
                        >
                            <span class="FavoritesPanelElement__name">
                                <span
                                    class="FavoritesPanelElement__type"
                                    :class="getContentType(favorite).modelName + 'Name'"
                                >
                                    {{ getContentType(favorite).name }}
                                </span>

                                <SmartLink :to="favorite.target_url">
                                    {{ favorite.target_name }}
                                </SmartLink>
                            </span>

                            <a
                                class="FavoritesPanelElement__remove"
                                @click="requestDeletion()"
                            >
                                X {{ $t("removeFavorite") }}
                            </a>
                        </div>
                    </Deletarium>
                </template>
            </template>
        </Loadarium>
    </div>
</MainLayout>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"
import MainLayout from "@components/layout/MainLayout"

export default {
    name: "FavoritesPanel",
    mixins: [PilotMixin],
    components: {
        MainLayout,
    },
    data: () => ({
        filteredFavorites: [],
    }),
    computed: {
        ...mapState("favorites", ["favorites"]),
        sortedFavorites() {
            return sortByAlphaString(this.favorites, (favorite) => favorite.target_name)
        },
    },
    methods: {
        ...mapActions("favorites", ["deleteFavorite"]),
        getContentType(favorite) {
            return _.find(this.contentTypes, { id: favorite.target_content_type_id })
        },
        onFuseResult(filteredFavorites) {
            this.filteredFavorites = filteredFavorites
        },
    },
    i18n: {
        messages: {
            fr: {
                removeFavorite: "Retirer",
                confirmRemoveFavorite: "Confirmer retirer de mes favoris ?",
                NoFavorites: "Vous n'avez aucun favori pour le moment",
            },
            en: {
                removeFavorite: "Remove",
                confirmRemoveFavorite: "Confirm remove from favorites ?",
                NoFavorites: "You have no favorites at the moment",
            },
        },
    },
}
</script>

<style lang="scss">
.FavoritesPanelElement {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    border-radius: 5px;
    margin-bottom: 0.5em;
    padding: 0.5em;
    background-color: #fcfcfc;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.FavoritesPanelElement__name {
    flex-grow: 1;
}

.FavoritesPanelElement__type {
    width: 70px;
    display: inline-block;
    text-align: center;
    font-size: 0.8em;
    font-weight: bold;
    padding: 0.2em 0.8em;
    border-radius: 10px;

    &.AssetName {
        background-color: rgba(249, 166, 47, 0.17);
        color: #e4982d;
    }
    &.ItemName {
        background-color: rgba(0, 172, 241, 0.29);
        color: rgb(0, 172, 241);
    }
    &.ProjectName {
        background-color: #e6beff;
        color: #8859f7;
    }
    &.ChannelName {
        background-color: rgb(200, 230, 201);
        color: rgb(27, 94, 32);
    }
}

.FavoritesPanelElement__remove {
    font-size: 0.8em;
}
.FavoritesPanelElement__EmptyState {
    @apply max-w-md text-lg text-gray-800 font-semibold leading-tight;
}
</style>
