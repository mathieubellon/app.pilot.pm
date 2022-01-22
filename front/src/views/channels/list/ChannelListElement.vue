<template>
<div class="ChannelListElement">
    <div class="px-4">
        <Icon
            name="Channel"
            size="20px"
        />
    </div>

    <div class="flex flex-grow flex-col truncate">
        <SmartLink
            class="Channel__title"
            :to="channel.url"
        >
            {{ channel.name }}
        </SmartLink>
        <div class="flex items-center text-sm font-medium text-gray-500">
            <p
                v-if="channel.search_headline"
                v-html="channel.search_headline"
                class="Channel__searchHeadline"
            />
        </div>
    </div>
    <div
        v-if="channel.type"
        class="w-40 flex-shrink-0 px-4"
    >
        <Label
            :goToListOnClick="true"
            :label="channel.type"
        />
    </div>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

import Label from "@views/labels/Label.vue"

export default {
    name: "ChannelListElement",
    mixins: [PilotMixin],
    components: {
        Label,
    },
    props: {
        channel: {
            type: Object,
            required: true,
        },
    },
}
</script>

<style lang="scss">
.ChannelListElement {
    @apply mb-2 w-full flex flex-grow w-full bg-white rounded border border-gray-300 items-center py-5;
}

.Channel__title {
    @apply text-gray-900 text-base font-semibold;

    &:hover {
        @apply text-blue-700 underline;
    }
}

.Channel__searchHeadline {
    font-size: 0.9em;

    .highlight {
        background: #ffff00;
        font-weight: bold;
    }
}
</style>
