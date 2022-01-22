<template>
<div class="AssetDetailOptions">
    <!-- NAME EDIT -->
    <button
        class="menu-item willClose"
        @click="setIsTitleInEdition(true)"
    >
        <Icon name="Edit" />
        {{ $t("editName") }}
    </button>

    <!-- FAVORITE -->
    <FavoriteToggle
        :contentType="contentTypes.Asset"
        :objectId="asset.id"
    />

    <!-- DELETE -->
    <MenuItemWithConfirm
        :confirmMessage="$t('thisActionCannotBeUndone')"
        :confirmTitle="$t('confirmAssetDeletion')"
        iconName="Trash"
        :isRed="true"
        :label="$t('deleteAsset')"
        loadingName="deleteAsset"
        @confirmed="onDeleteConfirmed()"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import FavoriteToggle from "@views/favorites/FavoriteToggle"
import MenuItemWithConfirm from "@components/MenuItemWithConfirm"

export default {
    name: "AssetDetailOptions",
    mixins: [PilotMixin],
    components: {
        FavoriteToggle,
        MenuItemWithConfirm,
    },
    computed: {
        ...mapState("assetDetail", ["asset"]),
    },
    methods: {
        ...mapMutations("assetDetail", ["setIsTitleInEdition"]),
        ...mapActions("assetDetail", ["deleteAsset"]),
        onDeleteConfirmed() {
            this.deleteAsset().then(() => {
                this.$router.push({ name: "assetList" })
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                confirmAssetDeletion: "Ce fichier sera définitivement supprimé !",
                deleteAsset: "Supprimer le fichier",
                editName: "Modifier le nom du fichier",
            },
            en: {
                confirmAssetDeletion: "Asset will be permanently deleted",
                deleteAsset: "Delete asset",
                editName: "Edit asset name",
            },
        },
    },
}
</script>

<style lang="scss">
.AssetDetailOptions {
    width: 18rem;
}
</style>
