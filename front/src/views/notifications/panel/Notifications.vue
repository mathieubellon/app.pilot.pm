<template>
<MainLayout>
    <template slot="title">
        <div class="flex items-center justify-between w-full">
            {{ $t("myNotifications") }}
        </div>
    </template>

    <template #actions>
        <button
            class="button"
            type="button"
            @click.prevent="openOffPanel('NotificationsSettingsPanel')"
        >
            {{ $t("notificationSettings") }}
        </button>
        <button
            class="button is-blue"
            :disabled="!unreadCount"
            type="button"
            @click.prevent="setAllRead()"
        >
            {{ $t("markAllAsRead") }}
        </button>
    </template>

    <template #middlebar>
        <div class="tabs">
            <a
                :class="['tab', { 'is-active': currentTab == 'unread' }]"
                @click.prevent="currentTab = 'unread'"
            >
                <span>{{ $t("unread") }}</span>
                ( {{ unreadCount }} )
            </a>

            <a
                :class="['tab', { 'is-active': currentTab == 'read' }]"
                @click.prevent="currentTab = 'read'"
            >
                <span>{{ $t("read") }}</span>
                ( {{ readCount }} )
            </a>
        </div>
    </template>

    <template #content>
        <div class="p-2 md:p-8 md:pr-4">
            <!-- Unread Tab -->
            <div
                v-if="currentTab == 'unread'"
                key="unreadTab"
            >
                <NotificationListTab listName="unread" />
            </div>

            <!-- Read tab -->
            <div
                v-if="currentTab == 'read'"
                key="readTab"
            >
                <NotificationListTab listName="read" />
            </div>
        </div>
    </template>
</MainLayout>
</template>

<script>
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

import NotificationListTab from "./NotificationListTab"
import MainLayout from "@components/layout/MainLayout"
import OffPanel from "@components/OffPanel.vue"

export default {
    name: "NotificationsPanel",
    mixins: [PilotMixin],
    components: {
        NotificationListTab,
        MainLayout,
        OffPanel,
    },
    data: () => ({
        currentTab: "unread",
    }),
    computed: {
        ...mapGetters("notifications", ["unreadCount", "readCount"]),
    },
    methods: {
        ...mapMutations("users", ["setUnreadNotificationCount"]),
        ...mapActions("notifications", ["fetchNotifications"]),
        fetchAllTabs() {
            this.fetchNotifications({ listName: "unread" })
            this.fetchNotifications({ listName: "read" })
        },
        setAllRead() {
            $httpX({
                name: "notificationsSetAllRead",
                commit: this.$store.commit,
                method: "POST",
                url: urls.notificationsSetAllRead,
            }).then((response) => {
                this.fetchAllTabs()
                this.setUnreadNotificationCount(0)
            })
        },
    },
    created() {
        this.fetchAllTabs()
    },
    i18n: {
        messages: {
            fr: {
                unread: "Non lues",
                read: "Lues",
                markAllAsRead: "Marquer tout comme lu",
                notificationSettings: "Gérer mes préférences de notification",
                myNotifications: "Mes notifications",
            },
            en: {
                unread: "Unread",
                read: "Read",
                markAllAsRead: "Mark all as read",
                notificationSettings: "Manage my notification preferences",
                myNotifications: "My notifications",
            },
        },
    },
}
</script>
