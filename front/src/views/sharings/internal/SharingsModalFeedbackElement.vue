<template>
<div class="text-sm p-1 bg-teal-50 mt-1">
    <div
        v-if="sharing.type != 'item'"
        class="mr-2"
    >
        {{ feedback.item.title }}
    </div>
    <span
        v-if="feedback.status == 'approved' || feedback.status == 'edited'"
        class="text-green-500 mr-2"
    >
        {{ $t("feedbackStatus.approved") }}
    </span>
    <span
        v-if="feedback.status == 'rejected'"
        class="text-red-500 mr-2"
    >
        {{ $t("feedbackStatus.rejected") }}
    </span>

    <span class="text-gray-700 mr-2">
        {{ feedback.created_at | dateTimeFormat }}
    </span>

    <Popper
        v-if="feedback.feedback_message"
        triggerElementName="FeedbackMessageRef"
    >
        <template #triggerElement>
            <button ref="FeedbackMessageRef">
                <Icon
                    class="text-gray-600 h-5 w-5 -mt-1"
                    name="Comment"
                />
            </button>
        </template>

        <template #content>
            <div style="width: 300px">
                {{ $t("contactLeftAMessage") }} {{ sharing.email }}

                <div class="bg-gray-200 p-2">
                    {{ feedback.feedback_message }}
                </div>
            </div>
        </template>
    </Popper>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "SharingsModalFeedbackElement",
    mixins: [PilotMixin],
    props: {
        feedback: Object,
        sharing: Object,
    },
    i18n: {
        messages: {
            fr: {
                contactLeftAMessage: "Message de ",
                feedbackStatus: {
                    approved: "Contenu validé",
                    rejected: "Contenu non validé",
                },
            },
            en: {
                contactLeftAMessage: "Message from ",
                feedbackStatus: {
                    approved: "Content validated",
                    rejected: "Content not validated",
                },
            },
        },
    },
}
</script>
