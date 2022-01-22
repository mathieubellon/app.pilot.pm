<template>
<div class="MainMenu">
    <Popper
        closeOnClickSelector=".willClose"
        placement="right"
        triggerElementName="UserPopper"
        :visibleArrow="false"
    >
        <template #triggerElement>
            <div
                class="MainMenu_element cursor-pointer flex-col"
                ref="UserPopper"
            >
                <a class="flex flex-col py-4">
                    <div class="flex items-center w-full">
                        <span class="sm:hidden xl:inline-block relative flex-shrink-0 mb-2">
                            <img
                                v-if="currentDesk.logoUrl"
                                class="h-6 w-6 rounded-full mr-2"
                                alt
                                :src="currentDesk.logoUrl"
                            />
                        </span>
                        <span
                            class="text-white text-base font-black leading-tight self-start flex sm:hidden xl:flex truncate"
                        >
                            {{ currentDesk.name }}
                        </span>
                    </div>

                    <div class="flex items-center justify-center w-full">
                        <span class="inline-block relative flex-shrink-0">
                            <img
                                v-if="users.me.avatar"
                                class="h-5 w-5 rounded-full"
                                :src="users.me.avatar"
                            />
                            <div
                                v-else
                                class="h-5 w-5 rounded-full bg-gray-300"
                            />
                            <span
                                class="absolute top-0 right-0 block h-1.5 w-1.5 rounded-full text-white shadow-solid bg-green-400"
                            />
                        </span>
                        <span class="MainMenu_element__name truncate">
                            <div
                                v-if="users.me.username"
                                class="truncate"
                            >
                                {{ users.me.username }}
                            </div>
                            <div
                                v-else
                                class="truncate"
                            >
                                loading username
                            </div>
                            <Icon
                                class="flex-shrink-0 text-white"
                                name="ChevronRight"
                                size="16px"
                            />
                        </span>
                    </div>
                </a>
            </div>
        </template>

        <template #content>
            <div class="flex flex-col items-start">
                <UserAvatar
                    class="h-10 w-10 rounded-full flex-no-shrink"
                    slot="buttonContent"
                    size="30px"
                    :user="users.me"
                />

                <div
                    v-if="users.me.first_name && users.me.last_name"
                    class="font-semibold text-gray-900 mb-3 leading-normal"
                >
                    {{ users.me.first_name }}&nbsp;{{ users.me.last_name }}
                    <br />
                    @{{ users.me.username }}
                </div>
                <a
                    class="menu-item willClose"
                    @click="openOffPanel('UserEditProfilePanel')"
                >
                    {{ $t("myAccount") }}
                </a>
                <a
                    class="menu-item willClose"
                    @click="openOffPanel('UserChangePasswordPanel')"
                >
                    {{ $t("editMyPassword") }}
                </a>
                <a
                    class="menu-item willClose"
                    @click="openOffPanel('NotificationsSettingsPanel')"
                >
                    {{ $t("notificationSettings") }}
                </a>

                <SmartLink
                    v-if="myPermissions.is_organization_admin"
                    class="menu-item willClose"
                    :to="urls.subscriptionApp.url"
                >
                    {{ $t("subscription") }}
                </SmartLink>

                <div class="font-bold text-sm mt-4 mb-2">{{ $t("myDesks") }}</div>

                <form
                    v-for="desk in users.me.desks"
                    class="w-full whitespace-no-wrap"
                    :action="urls.deskSwitch"
                    :key="desk.id"
                    method="POST"
                >
                    <input
                        name="csrfmiddlewaretoken"
                        type="hidden"
                        :value="csrfToken"
                    />
                    <input
                        name="desk_id"
                        type="hidden"
                        :value="desk.id"
                    />
                    <button
                        class="menu-item justify-between"
                        :class="{ 'bg-gray-200': desk.id == currentDesk.id }"
                        type="submit"
                    >
                        {{ desk.name }}
                        <div class="flex items-center">
                            <span
                                v-if="desk.unread_notifications_count"
                                class="flex rounded bg-red-600 text-white px-1 text-xs font-bold"
                            >
                                {{ desk.unread_notifications_count }}
                            </span>
                            <span
                                v-if="desk.undone_tasks_count"
                                class="flex rounded bg-orange-600 text-white px-1 text-xs font-bold ml-1"
                            >
                                {{ desk.undone_tasks_count }}
                            </span>
                        </div>
                    </button>
                </form>
                <a
                    v-if="myPermissions.is_organization_admin"
                    class="menu-item text-blue-600 hover:text-blue-900 hover:bg-transparent willClose"
                    @click="openOffPanel('newDesk')"
                >
                    {{ $t("newDesk") }}
                </a>
                <div class="w-full border-t border-gray-300 my-2" />
                <a
                    class="menu-item"
                    href="/logout/"
                >
                    {{ $t("logout") }}
                </a>
            </div>
        </template>
    </Popper>

    <div class="divider pt-2 border-t border-gray-600"></div>
    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'notifications' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('myNotifications') : ''"
    >
        <SmartLink to="/notifications">
            <Icon
                class="MainMenu_element__icon"
                :class="{ 'text-white': users.me.unread_notifications_count }"
                name="Bell"
            />
            <span
                class="MainMenu_element__name"
                :class="{ 'text-white': users.me.unread_notifications_count }"
            >
                {{ $t("myNotifications") }}
                <span
                    v-if="users.me.unread_notifications_count"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium leading-4 bg-gray-50 text-gray-800"
                >
                    {{ users.me.unread_notifications_count }}
                </span>
            </span>
        </SmartLink>
    </div>
    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'tasks' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('myTasks') : ''"
    >
        <SmartLink to="/tasks">
            <Icon
                class="MainMenu_element__icon"
                :class="{ 'text-white': users.me.undone_tasks_count }"
                name="Check"
            />
            <span
                class="MainMenu_element__name"
                :class="{ 'text-white': users.me.undone_tasks_count }"
            >
                {{ $t("myTasks") }}
                <span
                    v-if="users.me.undone_tasks_count"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium leading-4 bg-gray-50 text-gray-800"
                >
                    {{ users.me.undone_tasks_count }}
                </span>
            </span>
        </SmartLink>
    </div>
    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'favorites' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('myFavorites') : ''"
    >
        <SmartLink to="/favorites">
            <Icon
                class="MainMenu_element__icon"
                name="Star"
            />
            <span class="MainMenu_element__name">{{ $t("myFavorites") }}</span>
        </SmartLink>
    </div>
    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'search' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('search') : ''"
    >
        <SmartLink to="/search">
            <Icon
                class="MainMenu_element__icon"
                name="Search"
            />
            <span class="MainMenu_element__name">{{ $t("search") }}</span>
        </SmartLink>
    </div>
    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'dashboard' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('dashboard') : ''"
    >
        <SmartLink to="/dashboard">
            <Icon
                class="MainMenu_element__icon"
                name="Dashboard"
            />
            <span class="MainMenu_element__name">{{ $t("dashboard") }}</span>
        </SmartLink>
    </div>
    <div class="divider mt-2 pt-2 border-t border-gray-600"></div>
    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'projects' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('projects') : ''"
    >
        <SmartLink :to="urls.projectsApp.url">
            <Icon
                class="MainMenu_element__icon"
                name="Project"
            />
            <span class="MainMenu_element__name">{{ $t("projects") }}</span>
        </SmartLink>
    </div>
    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'items' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('allItems') : ''"
    >
        <SmartLink :to="urls.itemsApp.url">
            <Icon
                class="MainMenu_element__icon"
                name="Item"
            />
            <span class="MainMenu_element__name">{{ $t("items") }}</span>
        </SmartLink>
    </div>

    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'calendar' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('calendars') : ''"
    >
        <SmartLink :to="urls.calendarApp.url">
            <Icon
                class="MainMenu_element__icon"
                name="Calendar"
            />
            <span class="MainMenu_element__name">{{ $t("calendars") }}</span>
        </SmartLink>
    </div>
    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'channels' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('channels') : ''"
    >
        <SmartLink :to="urls.channelsApp.url">
            <Icon
                class="MainMenu_element__icon"
                name="Channel"
            />
            <span class="MainMenu_element__name">{{ $t("channels") }}</span>
        </SmartLink>
    </div>
    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'assets' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('assets') : ''"
    >
        <SmartLink :to="urls.assetsApp.url">
            <Icon
                class="MainMenu_element__icon"
                name="Asset"
            />
            <span class="MainMenu_element__name">{{ $t("assets") }}</span>
        </SmartLink>
    </div>
    <div
        class="MainMenu_element"
        :class="{ active: activeMenuElement == 'wiki' }"
        v-tooltip.right="viewportPhoneToLarge ? $t('wiki') : ''"
    >
        <SmartLink :to="urls.wikiApp.url">
            <Icon
                class="MainMenu_element__icon"
                name="Wiki"
            />
            <span class="MainMenu_element__name">{{ $t("wiki") }}</span>
        </SmartLink>
    </div>

    <!-- IF USER IS ADMIN -->
    <Popper
        placement="auto"
        triggerElementName="AdminPopper"
        :visibleArrow="false"
    >
        <template #triggerElement>
            <div
                class="MainMenu_element"
                :class="{ active: activeMenuElement == 'admin' }"
                ref="AdminPopper"
            >
                <a>
                    <Icon
                        class="MainMenu_element__icon"
                        name="Settings"
                    />
                    <span class="MainMenu_element__name">
                        {{ $t("settings") }}
                        <Icon
                            class="flex-shrink-0 text-white"
                            name="ChevronRight"
                            size="16px"
                        />
                    </span>
                </a>
            </div>
        </template>

        <template #content>
            <div class="flex flex-col items-start">
                <div class="font-bold text-md mb-2">
                    {{ $t("manageSettings") }}
                </div>
                <SmartLink
                    class="menu-item"
                    :to="urls.targetsApp.url"
                >
                    {{ $t("targets") }}
                </SmartLink>
                <SmartLink
                    class="menu-item"
                    :to="urls.labelsApp.url"
                >
                    {{ $t("labels") }}
                </SmartLink>
                <SmartLink
                    class="menu-item"
                    :to="urls.itemTypesApp.url"
                >
                    {{ $t("itemsTypes") }}
                </SmartLink>
                <SmartLink
                    class="menu-item"
                    :to="urls.taskGroupApp.url"
                >
                    {{ $t("taskGroup") }}
                </SmartLink>
                <SmartLink
                    class="menu-item"
                    :to="urls.workflowStatesApp.url"
                >
                    {{ $t("workflowStates") }}
                </SmartLink>

                <SmartLink
                    v-if="myPermissions.is_admin"
                    class="menu-item"
                    :to="urls.integrationsApp.url"
                >
                    {{ $t("integrations") }}
                </SmartLink>

                <SmartLink
                    v-if="myPermissions.is_admin"
                    class="menu-item"
                    :to="urls.sharingsApp.url"
                >
                    {{ $t("sharings") }}
                </SmartLink>

                <SmartLink
                    v-if="myPermissions.is_admin"
                    class="menu-item"
                    :to="urls.usersApp.url"
                >
                    {{ $t("users") }}
                </SmartLink>

                <SmartLink
                    v-if="myPermissions.is_admin"
                    class="menu-item"
                    :to="urls.deskApp.url"
                >
                    {{ $t("desk") }}
                </SmartLink>
            </div>
        </template>
    </Popper>

    <OffPanel
        name="newDesk"
        position="left"
        :width="'40%'"
    >
        <div slot="offPanelTitle">{{ $t("newDesk") }}</div>
        <div slot="offPanelBody">
            <DeskFormAdd />
        </div>
    </OffPanel>
</div>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import _ from "lodash"
import { csrfToken } from "@js/ajax"
import PilotMixin from "@components/PilotMixin"
import OffPanel from "@components/OffPanel.vue"

import DeskFormAdd from "@views/desk/DeskFormAdd.vue"

import UserAvatar from "@views/users/UserAvatar.vue"
import ResponsiveMixin from "@components/ResponsiveMixin"

export default {
    name: "MainMenu",
    mixins: [PilotMixin, ResponsiveMixin],
    components: {
        DeskFormAdd,
        UserAvatar,
        OffPanel,
    },
    data: () => ({
        csrfToken: csrfToken,
    }),
    computed: {
        ...mapState("favorites", ["favorites"]),
        ...mapGetters("users", ["myPermissions"]),
        users() {
            return this.$store.state.users
        },
        currentDeskInitials() {
            if (!this.currentDesk.name) return ""
            return this.currentDesk.name
                .split(" ")
                .map((n) => n[0])
                .join("")
        },
        activeMenuElement() {
            let routeMenuName = _.get(this, "$route.matched.0.meta.menu")
            return routeMenuName ? routeMenuName : window.pilot.activeMenu
        },
    },
    methods: {
        ...mapMutations("offPanel", ["openOffPanel"]),
    },
    i18n: {
        messages: {
            fr: {
                allItems: "Tous les contenus",
                editMyPassword: "Modifier mon mot de passe",
                logout: "Déconnexion",
                manageSettings: "Gestion des paramètres",
                myDesks: "Mes espaces de travail",
                notificationSettings: "Mes préférences de notification",
                settings: "Paramètres",
                subscription: "Mon abonnement",
            },
            en: {
                allItems: "All contents",
                editMyPassword: "Change my password",
                logout: "Logout",
                manageSettings: "Manage settings",
                myDesks: "Mes desks",
                notificationSettings: "My notification settings",
                settings: "Settings",
                subscription: "My subscription",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
@import "~@sass/include_media.scss";

.MainMenu {
    @apply flex flex-col overflow-hidden flex-shrink-0 p-0 m-0;
    background: #303e4d;
    width: 230px;

    @include media("<large") {
        width: 70px;
    }
}

.MainMenu_element {
    text-decoration: none;
    @apply flex items-center w-full mb-0.5;

    &:hover {
        a {
            @apply bg-gray-600 text-white;
        }
    }

    a {
        @apply px-5 flex items-center w-full text-gray-400 font-medium;
        @include media("<large") {
            @apply justify-center;
        }
    }

    &.active {
        a {
            @apply bg-blue-600 text-white font-black;
        }
    }
}

.MainMenu_element__name {
    @apply ml-3 text-sm font-semibold flex flex-grow items-center justify-between;
    &:first-letter {
        text-transform: capitalize;
    }

    @include media("<large") {
        display: none;
    }
    @include media("<phone") {
        display: flex;
        width: 100%;
    }
}

.MainMenu_element__icon {
    @apply flex-shrink-0 w-4 m-0.5;
    @include media("<large") {
        @apply w-5 m-1;
    }
}

.MainMenu .popper {
    @apply bg-white w-64;
}
</style>
