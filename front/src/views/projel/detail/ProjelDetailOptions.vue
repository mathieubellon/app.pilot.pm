<template>
<div class="ProjelDetailOptions">
    <button
        class="menu-item is-teal willClose"
        @click="$modal.show(isChannelRoute ? 'sharings-channel' : 'sharings-project')"
    >
        <Icon name="Share" />
        {{ $tc("sharingsButton", sharings.length, [sharings.length]) }}
    </button>

    <button
        class="menu-item willClose"
        @click="setIsNameInEdition(true)"
    >
        <Icon name="Edit" />
        {{ $t(isChannelRoute ? "editChannelName" : "editProjectName") }}
    </button>

    <FavoriteToggle
        :contentType="projelContentType"
        :objectId="projel.id"
    />

    <button
        v-if="isProjectRoute"
        class="menu-item willClose"
        @click="openOffPanel('copyProject')"
    >
        <Icon name="Copy" />
        {{ $t("copy") }}
    </button>

    <MenuItemWithConfirm
        v-if="projel.state != 'closed'"
        :confirmMessage="$t('youCanReopen')"
        :iconName="isChannelRoute ? 'Close' : 'ProjectClosed'"
        :label="$t(isChannelRoute ? 'closeChannel' : 'closeProject')"
        loadingName="closeProjel"
        @confirmed="closeProjel()"
    />

    <MenuItemWithConfirm
        :confirmMessage="$t('thisActionCannotBeUndone')"
        iconName="Trash"
        :isRed="true"
        :label="$t(isChannelRoute ? 'deleteChannel' : 'deleteProject')"
        loadingName="softDeleteProjel"
        @confirmed="onDeleteConfirmed"
    />
</div>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import PilotMixin from "@components/PilotMixin"
import MenuItemWithConfirm from "@components/MenuItemWithConfirm"

import FavoriteToggle from "@views/favorites/FavoriteToggle"

export default {
    name: "ProjelDetailOptions",
    mixins: [PilotMixin],
    components: {
        FavoriteToggle,
        MenuItemWithConfirm,
    },
    computed: {
        ...mapState("projelDetail", ["projel"]),
        ...mapGetters("projelDetail", ["isChannelRoute", "isProjectRoute", "projelContentType"]),
        ...mapState("sharings", ["sharings"]),
    },
    methods: {
        ...mapMutations("projelDetail", ["setIsNameInEdition"]),
        ...mapActions("projelDetail", ["closeProjel", "softDeleteProjel"]),
        onDeleteConfirmed() {
            this.softDeleteProjel().then(() => {
                let routeName = this.isChannelRoute ? "channelList-active" : "projectList-active"
                this.$router.push({ name: routeName })
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                closeChannel: "Fermer le canal",
                closeProject: "Fermer le projet",
                deleteChannel: "Supprimer le canal",
                deleteProject: "Supprimer le projet",
                editChannelName: "Modifier le nom du canal",
                editProjectName: "Modifier le nom du projet",
                youCanReopen: "Vous pourrez le ré-ouvrir plus tard.",
            },
            en: {
                closeChannel: "Close channel",
                closeProject: "Close project",
                deleteChannel: "Delete channel",
                deleteProject: "Delete project",
                editChannelName: "Edit channel name",
                editProjectName: "Edit project name",
                youCanReopen: "You can re-open it later",
            },
        },
    },
}
</script>

<style lang="scss">
.ProjelDetailOptions {
    width: 18rem;
}
</style>
