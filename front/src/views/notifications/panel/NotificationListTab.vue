<template>
<div class="NotificationListTab">
    <Loadarium name="fetchNotifications">
        <!-- Notification list -->
        <template v-if="notifications.length">
            <transition-group
                enter-active-class="animated fadeIn"
                leave-active-class="animated fadeOut"
            >
                <NotificationElement
                    v-for="notification in notifications"
                    :key="notification.id"
                    :listName="listName"
                    :notification="notification"
                />
            </transition-group>

            <div class="py-6">
                <button
                    v-if="pagination && notifications.length"
                    class="button"
                    :disabled="pagination.next === null"
                    @click="loadMoreButton()"
                >
                    <div v-if="pagination.next">
                        {{ $t("loadPage") }} {{ pagination.next }} / {{ pagination.num_pages }}
                    </div>
                    <div v-else>{{ $t("noMoreResults") }}</div>
                </button>
            </div>
        </template>

        <!-- No results -->
        <div
            v-else
            class="text-left text-2xl font-bold leading-tight mt-10"
        >
            <div v-html="$t('noMoreNotifications')"></div>
            <div class="text-3xl">👌</div>
        </div>
    </Loadarium>
</div>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

import NotificationElement from "./NotificationElement"

export default {
    name: "NotificationListTab",
    mixins: [PilotMixin],
    components: {
        NotificationElement,
    },
    props: {
        listName: String,
    },
    computed: {
        notifications() {
            return this.$store.state.notifications[this.listName].notifications
        },
        pagination() {
            return this.$store.state.notifications[this.listName].pagination
        },
    },
    methods: {
        ...mapActions("notifications", ["fetchNotifications"]),
        loadMoreButton() {
            this.fetchNotifications({
                listName: this.listName,
                append: true,
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                noNotification: "Aucune notification",
                noMoreNotifications: "Toutes les notifications sont lues. <br> Vous êtes à jour !",
            },
            en: {
                noNotification: "No notification",
                noMoreNotifications: "All notifications read. <br> You are up to date !",
            },
        },
    },
}
</script>

<style lang="scss">
.NotificationListTab__emptyState {
    font-size: 1.3em;
    margin: 3em 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}
</style>
