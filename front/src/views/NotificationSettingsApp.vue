<template>
<div class="NotificationSettingsApp">
    <div class="simple-panel NotificationSettingsApp__container">
        <h1>{{ $t("notificationPreferences") }}</h1>

        <div class="NotificationSettingsApp__description">
            <p>
                {{ $t("preferencesOfUser") }}
                <strong>{{ user.username }}</strong>
            </p>
            <p>{{ $t("notificationsDescription") }}</p>
        </div>

        <NotificationPreferencesToggles
            :notificationPreferences="user.notification_preferences"
            @toggleApp="toggleUserAppPreference"
            @toggleEmail="toggleUserEmailPreference"
        />
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

import NotificationPreferencesToggles from "@views/notifications/settings/NotificationPreferencesToggles"

export default {
    name: "NotificationSettingsApp",
    components: {
        NotificationPreferencesToggles,
    },
    computed: {
        user() {
            return window.notificationsSettingsContext.user
        },
    },
    methods: {
        toggleUserAppPreference(ptriggerElementName) {
            this.updateNotificationPreferences(ptriggerElementName, "app")
        },
        toggleUserEmailPreference(ptriggerElementName) {
            this.updateNotificationPreferences(ptriggerElementName, "email")
        },
        updateNotificationPreferences(ptriggerElementName, preferenceType) {
            this.user.notification_preferences[ptriggerElementName][preferenceType] = !Boolean(
                this.user.notification_preferences[ptriggerElementName][preferenceType],
            )
            $httpX({
                name: "updateNotificationPreferences",
                commit: this.$store.commit,
                method: "PATCH",
                url: urls.usersChangeNotificationPreferences.format({
                    token: window.notificationsSettingsContext.token,
                }),
                data: { notification_preferences: this.user.notification_preferences },
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                notificationPreferences: "Mes préférences de notification",
                notificationsDescription:
                    "Ces préfèrences peuvent être gérées depuis votre page de compte",
                preferencesOfUser: "Préférences de l'utilisateur",
            },
            en: {
                notificationPreferences: "My notification preferences",
                notificationsDescription: "These preferences can be managed from your account page",
                preferencesOfUser: "Preferences of user",
            },
        },
    },
}
</script>

<style lang="scss">
.NotificationSettingsApp {
    display: flex;
    justify-content: center;
}

.NotificationSettingsApp__container {
    width: 800px;
}
</style>
