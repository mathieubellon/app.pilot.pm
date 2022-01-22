<template>
<div class="ChannelPicker">
    <div class="flex items-center">
        <VueFuse
            class="flex-grow"
            :defaultAll="true"
            :keys="['name']"
            :list="channels"
            :placeholder="$t('search')"
            :threshold="0.1"
            @result="onFuseResult"
        />
    </div>
    <div class="Picker__List">
        <ChannelPickerElement
            v-for="channel in filteredChannels"
            :channel="channel"
            :disabled="loading"
            :key="channel.id"
            :loading="loading"
            :pickedChannel="getPickedChannel(channel.id)"
            :withHierarchy="withHierarchy"
            @pick="onPick"
            @unpick="onUnpick"
            @updatePick="onUpdatePick"
        />
    </div>

    <div
        v-if="channels.length == 0"
        class="help-text"
    >
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="Channel"
            />
            <span>{{ $t("noChannelYet") }}</span>
        </div>
        <SmartLink
            class="button is-blue"
            :to="urls.channelsApp.url"
        >
            {{ $t("createChannel") }}
        </SmartLink>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import PilotMixin from "@components/PilotMixin"

import ChannelPickerElement from "./ChannelPickerElement.vue"
import ButtonSpinner from "@components/ButtonSpinner"

export default {
    name: "ChannelPicker",
    mixins: [PilotMixin],
    components: {
        ButtonSpinner,
        ChannelPickerElement,
    },
    props: {
        channels: Array,
        // A list of PickedChannel instances
        pickedChannels: Array,
        loading: Boolean,
        withHierarchy: Boolean,
    },
    data: () => ({
        filteredChannels: [],
    }),
    methods: {
        onFuseResult(filteredChannels) {
            this.filteredChannels = filteredChannels
        },
        onPick(pickedChannel) {
            let pickedChannels = this.pickedChannels || []
            this.$emit("pick", [...pickedChannels, pickedChannel])
        },
        onUpdatePick(pickedChannel) {
            this.$emit(
                "pick",
                this.pickedChannels.map((oldPickedChannel) =>
                    oldPickedChannel.channelId == pickedChannel.channelId
                        ? pickedChannel
                        : oldPickedChannel,
                ),
            )
        },
        onUnpick(pickedChannel) {
            this.$emit(
                "pick",
                this.pickedChannels.filter((pc) => pc.channelId != pickedChannel.channelId),
            )
        },
        getPickedChannel(channelId) {
            return _.find(this.pickedChannels, { channelId })
        },
    },
    i18n: {
        messages: {
            fr: {
                createChannel: "Créer un canal",
                noChannelYet: "Vous n'avez pas encore créé de canal",
            },
            en: {
                createChannel: "Create a channel",
                noChannelYet: "You haven't created any channel yet",
            },
        },
    },
}
</script>
