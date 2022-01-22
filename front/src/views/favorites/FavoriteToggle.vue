<template>
<button
    class="menu-item"
    @click="toggleFavorite"
>
    <Icon
        :class="isFavored ? 'fill-current text-yellow-400' : ''"
        name="Star"
    />
    <Loadarium name="toggleFavorite">
        {{ $t(isFavored ? "removeFromFavorites" : "addToFavorites") }}
    </Loadarium>
</button>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

import PilotMixin from "@components/PilotMixin"

export default {
    name: "FavoriteToggle",
    mixins: [PilotMixin],
    props: {
        contentType: Object,
        objectId: Number,
    },
    computed: {
        ...mapState("favorites", ["favorites"]),
        existingFavorite() {
            return _.find(this.favorites, {
                target_content_type_id: this.contentType.id,
                target_object_id: this.objectId,
            })
        },
        isFavored() {
            return Boolean(this.existingFavorite)
        },
    },
    methods: {
        ...mapActions("favorites", ["createFavorite", "deleteFavorite"]),
        toggleFavorite() {
            if (this.isFavored) {
                this.deleteFavorite(this.existingFavorite)
            } else {
                this.createFavorite({
                    target_content_type_id: this.contentType.id,
                    target_object_id: this.objectId,
                })
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                addToFavorites: "Ajouter à mes favoris",
                removeFromFavorites: "Enlever de mes favoris",
            },
            en: {
                addToFavorites: "Add to my favorites",
                removeFromFavorites: "Remove from my favorites",
            },
        },
    },
}
</script>
