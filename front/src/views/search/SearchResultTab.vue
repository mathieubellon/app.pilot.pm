<template>
<div class="mt-3">
    <BarLoader
        v-if="docTypeData.showLoading"
        :color="colors.grey500"
        :width="100"
        widthUnit="%"
    />

    <div v-else>
        <!-- Error from the backend -->
        <div v-if="docTypeData.error">
            <div
                v-if="docTypeData.error.status == 400"
                class="text-red-600"
            >
                {{ $t("badRequest") }}
            </div>
            <div
                v-else-if="docTypeData.error.status == 503"
                class="text-red-600"
            >
                {{ $t("searchEngineUnreachable") }}
            </div>
            <div
                v-else
                class="text-red-600"
            >
                {{ $t("internalError") }}
            </div>
        </div>

        <!-- There is search results -->
        <div v-else-if="docTypeData.filteredUsers.length">
            <transition-group
                enter-active-class="animated fadeInUp"
                leave-active-class="animated fadeOutLeft"
            >
                <div
                    v-for="searchHit in docTypeData.filteredUsers"
                    :key="searchHit._source.id"
                >
                    <component
                        class=""
                        :is="hitDisplayComponent"
                        :searchHit="searchHit"
                    />
                </div>
            </transition-group>

            <button
                class="loadMoreButton button"
                :disabled="docTypeData.pagination.next === null"
                @click.prevent="$emit('loadMoreButton')"
            >
                <div v-if="docTypeData.pagination.next">
                    {{ $t("loadPage") }} {{ docTypeData.pagination.next }} /
                    {{ docTypeData.pagination.num_pages }}
                </div>
                <div v-else>{{ $t("noMoreResults") }}</div>
            </button>
        </div>

        <!-- No results -->
        <div v-else>
            {{ $t("noResults") }}
        </div>
    </div>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "SearchResultTab",
    mixins: [PilotMixin],
    props: {
        docTypeData: Object,
        hitDisplayComponent: Object,
    },
    i18n: {
        messages: {
            fr: {
                badRequest: "Je ne trouve rien parce que je ne comprend pas votre requête",
                loadPage: "Charger page",
                noMoreResults: "Pas de résultats supplémentaires",
                searchEngineUnreachable: "Le moteur de recherche est injoignable",
                internalError: "Erreur serveur interne",
            },
            en: {
                badRequest: "I don't understnd your request and can't find anything",
                loadPage: "Load page",
                noMoreResults: "No more results",
                searchEngineUnreachable: "Search engine unreachable",
                internalError: "Internal error",
            },
        },
    },
}
</script>
<style lang="scss">
@import "~@sass/include_media.scss";
.SearchResult {
    @apply mb-5 border border-gray-200 shadow p-5 rounded;
}
.SearchResult__Title {
    @apply font-bold text-lg;
}
.SearchResult__highlight {
    b {
        @apply bg-yellow-100 font-bold px-1;
    }
}
.SearchResult__ContentHits {
    @apply text-sm mt-1;
    .ContentHit {
        @apply text-gray-600;
    }
}

.SearchResult__InfosList {
    @apply flex items-center mt-2 items-stretch;
    .Info {
        @apply mr-2 px-1 text-xs bg-gray-100 text-gray-500 rounded-sm;
        .Info__value {
            @apply text-gray-800;
        }
    }
    @include media("<=phone") {
        @apply overflow-x-scroll;
    }
}
</style>
