<template>
<div
    v-if="notificationPreferences"
    class="NotificationPreferencesToggles"
>
    <template v-for="ptriggerElementName in ptriggerElementNames">
        <div class="NotificationSettingsLine">
            <div class="NotificationSettingsLine__Name">
                {{ $t("notifyWhen." + ptriggerElementName) }}
            </div>

            <div class="NotificationSettingsLine__actions">
                <div class="NotificationSettingsLine__toggle">
                    In-app
                    <ToggleButton
                        :labels="true"
                        :value="notificationPreferences[ptriggerElementName].app"
                        @change="$emit('toggleApp', ptriggerElementName)"
                    />
                </div>
                <div class="NotificationSettingsLine__toggle noDelete">
                    Email
                    <ToggleButton
                        :labels="true"
                        :value="notificationPreferences[ptriggerElementName].email"
                        @change="$emit('toggleEmail', ptriggerElementName)"
                    />
                </div>
            </div>
        </div>
    </template>
</div>
</template>

<script>
import { ToggleButton } from "vue-js-toggle-button"

const PREFERENCE_NAMES = ["mention", "reminder", "review", "task"]

export default {
    name: "NotificationPreferencesToggles",
    components: {
        ToggleButton,
    },
    props: {
        notificationPreferences: Object,
    },
    data: () => ({
        ptriggerElementNames: PREFERENCE_NAMES,
    }),
    i18n: {
        messages: {
            fr: {
                notifyWhen: {
                    mention: "Quand on me mentionne dans un commentaire",
                    reminder: "Quand l'un de mes rappel se déclenche",
                    review: "Quand je partage un contenu et que je reçois une réponse",
                    task: "Quand on m'affecte une tâche ou que mes tâches sont modifiées",
                },
            },
            en: {
                notifyWhen: {
                    mention: "When mentioned in a comment",
                    reminder: "When one of my reminders is triggered",
                    review: "When I share content and receive a response",
                    task: "When I am assigned a task or my tasks are modified",
                },
            },
        },
    },
}
</script>

<style lang="scss"></style>
