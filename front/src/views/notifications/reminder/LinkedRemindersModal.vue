<template>
<Modal
    height="auto"
    :name="`linkedReminders-${objectId}`"
    :pivotY="0.1"
>
    <div class="LinkedRemindersModal p-4">
        <a
            class="button is-small float-right"
            @click="$modal.hide(`linkedReminders-${objectId}`)"
        >
            {{ $t("close") }}
        </a>

        <div class="w-5/6 mb-6">
            <strong>{{ $t("reminders") }}</strong>
            <div>{{ $t("remindersHelpText") }}</div>
        </div>

        <div
            v-for="(reminder, index) in editedReminders"
            class="flex items-center w-full mb-4"
            :key="reminder.id"
        >
            <Icon
                class="mr-2"
                name="Bell"
            />

            <template v-if="reminder.is_notification_sent">
                <span>{{ reminder.delta_value }} {{ $t("deltaUnit." + reminder.delta_unit) }}</span>
                <span class="ml-4 text-green-500 font-bold">✓ {{ $t("notificationSent") }}</span>
            </template>

            <template v-else>
                <input
                    v-model="reminder.delta_value"
                    class="w-20 h-10 min-h-0"
                    type="text"
                />

                <select
                    v-model="reminder.delta_unit"
                    class="px-2"
                >
                    <option value="hours">{{ $t("deltaUnit.hours") }}</option>
                    <option value="days">{{ $t("deltaUnit.days") }}</option>
                    <option value="weeks">{{ $t("deltaUnit.weeks") }}</option>
                </select>

                <div class="px-2">{{ $t("before") }}</div>

                <a
                    class="button is-small ml-2"
                    @click="deleteReminder(index)"
                >
                    <Icon
                        class="text-red-600"
                        name="Trash"
                        size="15px"
                    />
                </a>
            </template>
        </div>

        <a
            class="indigo-link"
            @click="addReminder"
        >
            + {{ $t("addReminder") }}
        </a>

        <div class="flex justify-end mt-4">
            <button
                class="button"
                :disabled="isSaveDisabled"
                @click="cancelEdition"
            >
                {{ $t("cancel") }}
            </button>
            <ButtonSpinner
                class="button is-blue ml-4"
                :disabled="isSaveDisabled"
                :isLoading="isSaving"
                @click="saveReminders"
            >
                {{ $t("save") }}
            </ButtonSpinner>
        </div>
    </div>
</Modal>
</template>

<script>
import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import PilotMixin from "@components/PilotMixin"

import ButtonSpinner from "@components/ButtonSpinner"

const EMPTY_REMINDER = {
    delta_unit: "days",
    delta_value: "2",
}

export default {
    name: "LinkedRemindersModal",
    mixins: [PilotMixin],
    components: {
        ButtonSpinner,
    },
    props: {
        targetType: String,
        objectId: Number,
        reminders: Array,
    },
    data: () => ({
        isSaving: false,
        editedReminders: [],
    }),
    computed: {
        isSaveDisabled() {
            return _.isEqual(this.reminders, this.editedReminders)
        },
    },
    methods: {
        addReminder() {
            let newReminder = _.clone(EMPTY_REMINDER)
            this.editedReminders.push(newReminder)
        },
        deleteReminder(index) {
            this.editedReminders.splice(index, 1)
        },
        saveReminders() {
            this.isSaving = true
            let promises = []

            for (let editedReminder of this.editedReminders) {
                // CREATE
                if (!editedReminder.id) {
                    promises.push(
                        $httpX({
                            name: "addReminder",
                            commit: this.$store.commit,
                            method: "POST",
                            url: urls.reminders,
                            data: {
                                ...editedReminder,
                                target_type: this.targetType,
                                object_id: this.objectId,
                            },
                        }),
                    )
                }

                // UPDATE
                else if (
                    !_.isEqual(
                        editedReminder,
                        _.find(this.reminders, (r) => r.id == editedReminder.id),
                    )
                ) {
                    promises.push(
                        $httpX({
                            name: "saveReminders",
                            commit: this.$store.commit,
                            method: "PATCH",
                            url: urls.reminders.format({ id: editedReminder.id }),
                            data: editedReminder,
                        }),
                    )
                }
            }

            //  DELETE
            for (let reminder of this.reminders) {
                if (!_.find(this.editedReminders, (r) => r.id == reminder.id)) {
                    promises.push(
                        $httpX({
                            name: "deleteReminder",
                            commit: this.$store.commit,
                            method: "DELETE",
                            url: urls.reminders.format({ id: reminder.id }),
                        }),
                    )
                }
            }

            Promise.all(promises).then(() => {
                this.isSaving = false
                this.reminders.splice(0, this.reminders.length, ...this.editedReminders)
            })
        },
        cancelEdition() {
            this.editedReminders = _.cloneDeep(this.reminders)
        },
    },
    created() {
        this.editedReminders = _.cloneDeep(this.reminders)
    },
    i18n: {
        messages: {
            fr: {
                addReminder: "Ajouter un rappel",
                before: "avant",
                deltaUnit: {
                    days: "Jours",
                    hours: "Heures",
                    weeks: "Semaines",
                },
                notificationSent: "Notification envoyée",
                remindersHelpText:
                    "Les rappels sont visibles uniquement par vous. Vous seul.e recevrez les notifications programmées ci-dessous.",
                reminderSaveOk: "Rappels sauvegardés",
            },
            en: {
                addReminder: "Add reminder",
                before: "before",
                deltaUnit: {
                    days: "Days",
                    hours: "Hours",
                    weeks: "Weeks",
                },
                notificationSent: "Notification sent",
                remindersHelpText:
                    "Reminders are only visible to you. Only you will receive the notifications scheduled below.",
                reminderSaveOk: "Reminders saved",
            },
        },
    },
}
</script>
