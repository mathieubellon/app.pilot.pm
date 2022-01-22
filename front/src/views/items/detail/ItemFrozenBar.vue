<template>
<div
    v-if="item.frozen"
    class="flex flex-col justify-center items-center bg-yellow-200 p-2"
>
    <div class="inline-flex items-center">
        <Icon
            class="mr-2 -ml-6"
            name="LockClosed"
        />
        {{ $t("itemIsFrozen") }}
        <UserDisplay
            aClass="font-semibold ml-1 mr-1"
            :user="item.frozen_by"
        />
        {{ $t("at") }}
        <span class="font-semibold ml-1">{{ item.frozen_at | dateTimeFormat }}</span>
    </div>

    <div
        v-if="messageHtml"
        v-html="messageHtml"
        class="RichTextStyling w-full max-w-xl mt-2 px-2 rounded border border-gray-300 bg-gray-50"
    />
</div>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import { richTextSchema } from "@richText/schema"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ItemFrozenBar",
    mixins: [PilotMixin],
    props: {
        item: Object,
    },
    computed: {
        messageHtml() {
            return richTextSchema.HTMLFromJSON(this.item.frozen_message)
        },
    },
    i18n: {
        messages: {
            fr: {
                itemIsFrozen: "Édition verrouillée par",
            },
            en: {
                itemIsFrozen: "Edition locked by",
            },
        },
    },
}
</script>
