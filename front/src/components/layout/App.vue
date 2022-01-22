<template>
<div id="app">
    <!-- Main Menu on the left -->
    <template v-if="!isAnonymousUser">
        <MainMenu v-show="viewportGTEPhone" />
        <MainMenuMobile v-show="!viewportGTEPhone" />
    </template>

    <!-- Main content on the right -->
    <NotFoundComponent v-if="objectNotFound" />
    <slot
        v-else
        name="main"
    />

    <!-- General panels/modals -->
    <UserEditProfilePanel key="UserEditProfilePanel" />
    <UserChangePasswordPanel key="UserChangePasswordPanel" />
    <NotificationsSettingsPanel key="NotificationsSettingsPanel" />
    <UserExaminationPanel key="UserExaminationPanel" />
    <ItemPreviewModal key="ItemPreviewModal" />
    <ItemBulkUpdatePanel key="ItemBulkUpdatePanel" />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

import ResponsiveMixin from "@components/ResponsiveMixin"

import MainMenu from "./MainMenu"
import MainMenuMobile from "./MainMenuMobile.vue"
import NotFoundComponent from "@components/NotFoundComponent"

import UserEditProfilePanel from "@views/users/panels/UserEditProfilePanel"
import UserChangePasswordPanel from "@views/users/panels/UserChangePasswordPanel"
import UserExaminationPanel from "@views/users/panels/UserExaminationPanel"
import NotificationsSettingsPanel from "@views/notifications/settings/NotificationsSettingsPanel"
import ItemPreviewModal from "@views/items/ItemPreviewModal"
import ItemBulkUpdatePanel from "@views/items/list/ItemBulkUpdatePanel"

export default {
    name: "App",
    mixins: [ResponsiveMixin],
    components: {
        MainMenu,
        MainMenuMobile,
        NotFoundComponent,
        UserEditProfilePanel,
        UserChangePasswordPanel,
        UserExaminationPanel,
        NotificationsSettingsPanel,
        ItemPreviewModal,
        ItemBulkUpdatePanel,
    },
    data: () => ({
        isAnonymousUser: window.pilot.user.isAnonymous,
    }),
    computed: {
        ...mapState(["objectNotFound"]),
    },
}
</script>
