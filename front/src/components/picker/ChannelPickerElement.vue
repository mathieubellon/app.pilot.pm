<template>
<div class="flex-col mt-2">
    <div
        v-if="loading && lastClickedElement == channel"
        class="ChannelPicker__Element"
    >
        <BarLoader
            color="#3182CE"
            :loading="true"
            :width="100"
            widthUnit="%"
        />
    </div>
    <div
        v-else
        class="ChannelPicker__Element justify-between"
        :class="{ picked: isRootFolderPicked, disabled }"
        :disbaled="disabled"
        @click="onChannelClick"
    >
        <div class="Picker__Element__Name">
            <input
                :checked="isRootFolderPicked"
                type="checkbox"
            />
            <div>{{ channel.name }}</div>
        </div>
        <div
            v-if="channel.type"
            class="Picker__Element__Type"
        >
            {{ channel.type.name }}
        </div>
    </div>

    <div v-if="withHierarchy">
        <div
            v-for="folder in folders"
            class="ChannelPicker__Element"
            :class="{ picked: isFolderPicked(folder) }"
            @click="onFolderClick(folder)"
        >
            <div
                v-if="loading && lastClickedElement == folder"
                class="ChannelPicker__Element"
            >
                <BarLoader
                    color="#3182CE"
                    :loading="true"
                    :width="100"
                    widthUnit="%"
                />
            </div>
            <div
                v-else
                class="Picker__Element__Name"
            >
                <input
                    :checked="isFolderPicked(folder)"
                    type="checkbox"
                />
                <!-- Spacer for visual indentation of subfolders -->
                <span
                    v-for="level in folder.level"
                    class="flex-shrink-0 w-4"
                />
                <div class="pl-8 text-sm leading-6 px-2">
                    {{ folder.name | defaultVal("N/A") }}
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import { flattenHierarchy, getFolderPath, NODE_TYPES } from "@js/hierarchy"
import HierarchyMixin from "@views/projel/HierarchyMixin"

import { BarLoader } from "@saeris/vue-spinners"

/**
 * Data representing a picked channel,
 * with the channel id and an optionnal folder path ( an array of folder names )
 */
export class PickedChannel {
    constructor(channelId, folderPath = null) {
        this.channelId = channelId
        this.folderPath = folderPath
    }
}

export default {
    name: "ChannelPickerElement",
    mixins: [HierarchyMixin],
    components: {
        BarLoader,
    },
    props: {
        channel: Object,
        // If this.channel is picked, this prop will hold a PickedChannel instance
        pickedChannel: Object,
        disabled: Boolean,
        withHierarchy: Boolean,
        loading: Boolean,
    },
    data: () => ({
        lastClickedElement: null,
    }),
    computed: {
        isChannelPicked() {
            return Boolean(this.pickedChannel)
        },
        isRootFolderPicked() {
            return this.isChannelPicked && _.isEmpty(this.pickedChannel.folderPath)
        },
        folders() {
            return flattenHierarchy(this.hierarchy).filter(
                // Show only folders
                (node) => node.type == NODE_TYPES.folder,
            )
        },
    },
    methods: {
        isFolderPicked(folder) {
            if (!this.isChannelPicked) {
                return false
            }
            return _.isEqual(getFolderPath(folder), this.pickedChannel.folderPath)
        },
        onChannelClick() {
            if (!this.disabled) {
                this.lastClickedElement = this.channel
                if (this.isRootFolderPicked) {
                    this.$emit("unpick", new PickedChannel(this.channel.id))
                } else if (this.isChannelPicked) {
                    this.$emit("updatePick", new PickedChannel(this.channel.id))
                } else {
                    this.$emit("pick", new PickedChannel(this.channel.id))
                }
            }
        },
        onFolderClick(folder) {
            let folderPath = getFolderPath(folder)
            if (!this.disabled) {
                this.lastClickedElement = folder
                // Unpick the folder and channel
                if (this.isFolderPicked(folder)) {
                    this.$emit("unpick", new PickedChannel(this.channel.id))
                }
                // Keep the channel picked, and update the picked folder
                else if (this.isChannelPicked) {
                    this.$emit("updatePick", new PickedChannel(this.channel.id, folderPath))
                }
                // Pick the channel and the folder
                else {
                    this.$emit("pick", new PickedChannel(this.channel.id, folderPath))
                }
            }
        },
    },
    created() {
        this.initHierarchy(this.channel.hierarchy)
    },
}
</script>

<style lang="scss">
@import "~@sass/picker.scss";

.ChannelPicker__Element {
    @extend .Picker__Element;
    @apply justify-between mb-0 h-8 rounded-none;
}
</style>
