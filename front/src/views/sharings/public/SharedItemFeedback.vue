<template>
<div class="SharedItemFeedback">
    <div
        v-if="feedback"
        class="alert-panel is-green p-2 -mt-1 mb-0 inline-block"
    >
        ✓ {{ $t("feedbackSuccess") }}
        {{ $t("contactHasBeenNotified") }}
    </div>

    <div
        v-else
        class="flex items-center h-8"
    >
        <!-- Already replied : the buttons are hidden -->
        <template v-if="feedback">
            {{ $t("alreadyReplied") }}
        </template>

        <!-- Not yet replied : the buttons are visible -->
        <template v-else>
            <button
                class="button is-green mr-2"
                @click="approve()"
            >
                {{ $t("validate") }}
            </button>
            <button
                class="button is-orange"
                @click="reject()"
            >
                {{ $t("reject") }}
            </button>
        </template>
    </div>

    <Modal
        name="sharingFeedback"
        height="auto"
        :pivotY="0.1"
    >
        <div class="p-8">
            <div class="font-semibold">
                <template v-if="sharing.is_editable">{{ $t("notification.editable") }}</template>
                <template v-else-if="status == 'approved'">
                    {{ $t("notification.readOnlyApproved") }}
                </template>
                <template v-else-if="status == 'rejected'">
                    {{ $t("notification.readOnlyRejected") }}
                </template>
                <br />
                {{ $t("notification.youCanMessage") }}
            </div>

            <TextAreaAutosize
                v-model="feedbackMessage"
                class="w-full my-4"
                :placeholder="$t('message')"
            />

            <SmartButtonSpinner
                class="mr-4"
                :class="{
                    'is-green': status == 'approved',
                    'is-red': status == 'rejected',
                }"
                name="saveSharing"
                @click="sendFeedback"
            >
                {{ $t("okSendFeedback") }}
            </SmartButtonSpinner>
            <button
                class="button"
                type="button"
                @click="$modal.hide('sharingFeedback')"
            >
                {{ $t("cancel") }}
            </button>
        </div>
    </Modal>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "SharedItemFeedback",
    mixins: [PilotMixin],
    data: () => ({
        feedbackMessage: "",
        status: "",
    }),
    computed: {
        ...mapState(["sharing"]),
        ...mapGetters("sharedItem", ["feedback"]),
        ...mapState("itemContentForm", ["validation"]),
    },
    methods: {
        ...mapActions("sharedItem", ["createItemFeedback"]),
        approve() {
            this.status = "approved"
            this.$modal.show("sharingFeedback")
        },
        reject() {
            this.status = "rejected"
            this.$modal.show("sharingFeedback")
        },
        sendFeedback() {
            this.createItemFeedback({
                status: this.status,
                feedbackMessage: this.feedbackMessage,
            }).then(() => this.$modal.hide("sharingFeedback"))
        },
    },
    i18n: {
        messages: {
            fr: {
                alreadyReplied: "Le contenu a déjà été validé ou rejeté",
                contactHasBeenNotified: "Votre contact a été notifié.",
                feedbackSuccess: "Votre retour a bien été pris en compte.",
                message: "Message optionnel",
                notification: {
                    editable: "Votre contact sera informé que vous avez modifié le contenu.",
                    readOnlyApproved: "Votre contact sera informé que vous validez ce contenu.",
                    readOnlyRejected:
                        "Votre contact sera informé que vous ne validez pas ce contenu.",
                    youCanMessage: "Vous pouvez aussi lui laisser un message si vous le souhaitez.",
                },
                okSendFeedback: "Ok, envoyer",
                reject: "Ne pas valider le contenu",
                validate: "Valider le contenu",
            },
            en: {
                alreadyReplied: "The content is already validated or rejected",
                contactHasBeenNotified: "Your contact has been notified.",
                feedbackSuccess: "Feedback successfully sent.",
                message: "Optionnal feedback",
                notification: {
                    editable: "You contact will be notified that you edited the content.",
                    readOnlyApproved: "You contact will be notified that you validate the content.",
                    readOnlyRejected:
                        "You contact will be notified that you do not validate the content.",
                    youCanMessage: "You can also give him some feedback if you wish.",
                },
                okSendFeedback: "Ok, send",
                reject: "Do not validate the content",
                validate: "Validate the content",
            },
        },
    },
}
</script>
