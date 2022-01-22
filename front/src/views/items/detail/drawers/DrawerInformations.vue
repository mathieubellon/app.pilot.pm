<template>
<div class="ItemDrawer DrawerInformations">
    <div class="ItemDrawer__Header">
        {{ $t("informations") }}

        <div
            class="font-medium text-sm cursor-pointer hover:text-blue-600"
            @click="closePanel()"
        >
            {{ $t("close") }}
        </div>
    </div>
    <!--State dropdown-->
    <div class="my-3">
        <ItemStateDropdown
            :inactiveMentionGroups="inactiveMentionGroups"
            :item="item"
            referenceClass="px-1 py-2 text-base font-medium bg-white border-gray-200"
            @saved="onStateSaved"
        />
    </div>

    <!-- Project Picker -->
    <div class="MetadataBlock">
        <div class="MetadataBlock__Header">
            <Icon
                class="MetadataBlock__Icon"
                name="Project"
            />
            {{ labels.project }}
            <a
                v-if="!item.in_trash"
                class="MetadataBlock__Settings"
                @click.prevent="openOffPanel('projectPicker')"
            >
                <Icon
                    class="w-4"
                    name="Settings"
                />
            </a>
        </div>

        <transition
            enter-active-class="animated fadeIn"
            leave-active-class="animated fadeOut"
            mode="out-in"
        >
            <BarLoader
                v-if="fieldsCurrentlyUpdating.project_id"
                class="my-3"
                key="barLoader"
                color="#3182CE"
                :loading="true"
                :width="100"
                widthUnit="%"
            />
            <div
                v-else-if="item.project_id"
                class="flex flex-col w-full"
                :key="item.project_id"
            >
                <div class="Metadata">
                    <SmartLink
                        class="Metadata__Name"
                        :to="item.project.url"
                    >
                        {{ item.project.name }}
                    </SmartLink>

                    <span
                        class="Metadata__HierarchyPath"
                        :title="getHierarchyPath(item.project)"
                    >
                        {{ getHierarchyPath(item.project) }}
                    </span>

                    <a @click="showProjectDetails = !showProjectDetails">
                        <Icon
                            v-if="showProjectDetails"
                            class="w-4"
                            name="ChevronUp"
                        />
                        <Icon
                            v-else
                            class="w-4"
                            name="ChevronDown"
                        />
                    </a>
                    <a @click="onProjectPicked(item.project)">
                        <Icon
                            class="w-4"
                            name="Close"
                        />
                    </a>
                </div>

                <div
                    v-if="showProjectDetails"
                    class="Metadata__Details"
                >
                    <div class="mb-2">
                        <div class="text-sm font-semibold text-gray-900">
                            {{ $t("description") }}
                        </div>
                        <div
                            v-if="projectDescriptionHtml"
                            v-html="projectDescriptionHtml"
                            class="text-base font-normal text-gray-700"
                        />
                        <span v-else>{{ $t("noDescription") }}</span>
                    </div>
                    <div v-if="item.project.items">
                        <div class="text-sm font-semibold text-gray-900">
                            {{ $t("itemsInProject") }}
                        </div>
                        <div
                            v-for="projectItem in item.project.items"
                            class="text-sm text-gray-900 mb-1"
                        >
                            <SmartLink :to="projectItem.url">
                                {{ projectItem.title | defaultVal("N/A") }}
                            </SmartLink>
                            <!--<br />-->
                            <!--#{{ projectItem.id }} |-->
                            <!--<template v-if="projectItem.language">{{ projectItem.language }} |</template>-->
                            <!--{{ projectItem.updated_at | dateTimeFormat }}-->
                        </div>
                    </div>
                </div>
            </div>
            <div
                v-else
                class="MetadataBlock__empty"
                key="empty"
            >
                {{ $t("noProject") }}
            </div>
        </transition>

        <OffPanel name="projectPicker">
            <div slot="offPanelTitle">{{ $t("selectProject") }}</div>
            <ProjectPicker
                slot="offPanelBody"
                :pickedProject="item.project"
                :projects="choices.projects"
                @pick="onProjectPicked"
            />
        </OffPanel>
    </div>
    <!-- Channel Picker -->
    <div class="MetadataBlock">
        <div class="MetadataBlock__Header">
            <Icon
                class="MetadataBlock__Icon"
                name="Channel"
            />
            {{ labels.channels }}
            <a
                v-if="!item.in_trash"
                class="MetadataBlock__Settings"
                @click.prevent="openOffPanel('channelPicker')"
            >
                <Icon
                    class="w-4"
                    name="Settings"
                />
            </a>
        </div>
        <transition-group
            enter-active-class="animated fadeIn"
            leave-active-class="animated fadeOut"
            mode="out-in"
        >
            <div
                v-for="channel in sortedChannels"
                :key="channel.id"
            >
                <BarLoader
                    v-if="
                        fieldsCurrentlyUpdating.channels_id && currentUpdatedChannel === channel.id
                    "
                    class="my-3"
                    color="#3182CE"
                    :loading="true"
                    :width="80"
                    widthUnit="%"
                />
                <div
                    v-else
                    class="flex flex-col w-full"
                >
                    <div class="Metadata">
                        <SmartLink
                            class="Metadata__Name"
                            :to="channel.url"
                        >
                            {{ channel.name }}
                        </SmartLink>

                        <span
                            class="Metadata__HierarchyPath"
                            :title="getHierarchyPath(channel)"
                        >
                            {{ getHierarchyPath(channel) }}
                        </span>

                        <a
                            @click="
                                showChannelDetails =
                                    showChannelDetails == channel.id ? null : channel.id
                            "
                        >
                            <Icon
                                v-if="showChannelDetails == channel.id"
                                class="w-4"
                                name="ChevronUp"
                            />
                            <Icon
                                v-else
                                class="w-4"
                                name="ChevronDown"
                            />
                        </a>
                        <a
                            class=""
                            @click="removeChannel(channel)"
                        >
                            <Icon
                                class="w-4"
                                name="Close"
                            />
                        </a>
                    </div>

                    <div
                        v-if="showChannelDetails == channel.id"
                        class="Metadata__Details"
                    >
                        <div class="text-sm font-bold text-gray-900">{{ $t("description") }}</div>
                        <div
                            v-if="getChannelDescriptionHtml(channel)"
                            v-html="getChannelDescriptionHtml(channel)"
                            class="text-sm font-normal text-gray-700"
                        />
                        <span v-else>{{ $t("noDescription") }}</span>
                    </div>
                </div>
            </div>
        </transition-group>
        <div
            v-if="sortedChannels.length === 0"
            class="MetadataBlock__empty"
        >
            {{ $t("noChannel") }}
        </div>

        <OffPanel name="channelPicker">
            <div slot="offPanelTitle">{{ $t("selectChannels") }}</div>
            <ChannelPicker
                slot="offPanelBody"
                :channels="choices.channels"
                :loading="fieldsCurrentlyUpdating.channels_id"
                :pickedChannels="pickedChannels"
                :withHierarchy="true"
                @pick="onChannelPicked"
            />
        </OffPanel>
    </div>

    <!-- Targets Picker -->
    <div class="MetadataBlock">
        <div class="MetadataBlock__Header">
            <Icon
                class="MetadataBlock__Icon"
                name="Target"
            />
            {{ labels.targets }}
            <a
                v-if="!item.in_trash"
                class="MetadataBlock__Settings"
                @click.prevent="openOffPanel('targetPicker')"
            >
                <Icon
                    class="w-4"
                    name="Settings"
                />
            </a>
        </div>
        <transition-group
            enter-active-class="animated fadeIn"
            leave-active-class="animated fadeOut"
        >
            <div
                v-for="target in sortedTargets"
                :key="target.id"
            >
                <BarLoader
                    v-if="fieldsCurrentlyUpdating.targets_id && currentUpdatedTarget === target.id"
                    class="my-3"
                    color="#3182CE"
                    :loading="true"
                    :width="100"
                    widthUnit="%"
                />
                <div
                    v-else
                    class="Metadata"
                >
                    <SmartLink
                        class="Metadata__Name flex-grow"
                        :to="urls.targetsApp.url"
                    >
                        {{ target.name }}
                    </SmartLink>
                    <a
                        class=""
                        @click="removeTarget(target)"
                    >
                        <Icon
                            class="w-4"
                            name="Close"
                        />
                    </a>
                </div>
            </div>
        </transition-group>
        <div
            v-if="sortedTargets.length === 0"
            class="MetadataBlock__empty"
        >
            {{ $t("noTarget") }}
        </div>

        <OffPanel name="targetPicker">
            <div slot="offPanelTitle">{{ $t("selectTarget") }}</div>
            <TargetPicker
                slot="offPanelBody"
                :loading="fieldsCurrentlyUpdating.targets_id"
                :multiple="true"
                :pickedTargetsId="item.targets_id"
                :targets="choices.targets"
                @pick="onTargetPicked"
            />
        </OffPanel>
    </div>

    <!-- Owners Picker -->
    <div class="MetadataBlock">
        <div class="MetadataBlock__Header">
            <Icon
                class="MetadataBlock__Icon"
                name="Users"
            />
            {{ labels.owners }}
            <a
                v-if="!item.in_trash"
                class="MetadataBlock__Settings"
                @click.prevent="openOffPanel('ownerPicker')"
            >
                <Icon
                    class="w-4"
                    name="Settings"
                />
            </a>
        </div>
        <transition-group
            enter-active-class="animated fadeInUp"
            leave-active-class="animated fadeOutDown"
        >
            <div
                v-for="owner in sortedOwners"
                :key="owner.id"
            >
                <BarLoader
                    v-if="fieldsCurrentlyUpdating.owners_id && currentUpdatedOwner === owner.id"
                    class="my-3"
                    color="#3182CE"
                    :loading="true"
                    :width="100"
                    widthUnit="%"
                />
                <div
                    v-else
                    class="Metadata"
                >
                    <div class="Metadata__Name -ml-1 flex-grow">
                        <UserDisplay
                            :user="owner"
                            :withAvatar="true"
                        />
                    </div>
                    <a @click.stop.prevent="removeOwner(owner)">
                        <Icon
                            class="w-4"
                            name="Close"
                        />
                    </a>
                </div>
            </div>
        </transition-group>
        <div
            v-if="sortedOwners.length === 0"
            class="MetadataBlock__empty"
        >
            {{ $t("noOwner") }}
        </div>

        <OffPanel name="ownerPicker">
            <div slot="offPanelTitle">{{ $t("selectOwners") }}</div>
            <UserPicker
                slot="offPanelBody"
                :loading="fieldsCurrentlyUpdating.owners_id"
                :multiple="true"
                :pickedUsersId="item.owners_id"
                :users="choices.users"
                @pick="onOwnerPicked"
            />
        </OffPanel>
    </div>

    <!-- Tags Picker -->
    <div class="MetadataBlock">
        <div class="MetadataBlock__Header">
            <Icon
                class="MetadataBlock__Icon"
                name="Tag"
            />
            {{ labels.tags }}
            <LabelSelect
                v-if="!item.in_trash"
                boundariesSelector="body"
                :isUpdating="fieldsCurrentlyUpdating.tags_id"
                :multiple="true"
                placement="right"
                :sortable="false"
                targetType="item_tags"
                triggerElementName="PopperRef"
                :value="item.tags"
                @input="onTagsInput"
            >
                <template #triggerElement>
                    <a
                        class="MetadataBlock__Settings"
                        ref="PopperRef"
                    >
                        <Icon
                            class="w-4"
                            name="Settings"
                        />
                    </a>
                </template>
            </LabelSelect>
        </div>
        <transition-group
            class="flex flex-wrap"
            enter-active-class="animated fadeInUp"
            leave-active-class="animated fadeOutDown"
            tag="div"
        >
            <Label
                v-for="tag in item.tags"
                :goToListOnClick="true"
                :key="tag.id"
                :label="tag"
            />
        </transition-group>
        <div
            v-if="item.tags.length === 0"
            class="MetadataBlock__empty"
        >
            {{ $t("noTag") }}
        </div>
    </div>

    <!-- Type -->
    <div class="MetadataBlock">
        <div class="MetadataBlock__Header">
            {{ $t("contentType") }}
        </div>
        <SmartLink
            v-if="item.item_type"
            class="w-full"
            :to="item.item_type.url"
        >
            {{ item.item_type.name }}
        </SmartLink>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { sortByAlphaString } from "@js/utils.js"
import { richTextSchema } from "@richText/schema"
import { getItemPathInHierarchy } from "@js/hierarchy"
import PilotMixin from "@components/PilotMixin"

import ProjectPicker from "@components/picker/ProjectPicker.vue"
import ChannelPicker from "@components/picker/ChannelPicker.vue"
import { PickedChannel } from "@components/picker/ChannelPickerElement.vue"
import TargetPicker from "@components/picker/TargetPicker.vue"
import UserPicker from "@components/picker/UserPicker.vue"
import ItemPicker from "@components/picker/ItemPicker.vue"
import Label from "@views/labels/Label.vue"
import LabelSelect from "@views/labels/LabelSelect.vue"
import ItemStateDropdown from "@views/items/ItemStateDropdown.vue"

export default {
    name: "DrawerInformations",
    mixins: [PilotMixin],
    components: {
        ProjectPicker,
        ChannelPicker,
        TargetPicker,
        UserPicker,
        ItemPicker,
        Label,
        LabelSelect,
        ItemStateDropdown,
    },
    data: () => ({
        showProjectDetails: false,
        showChannelDetails: false,
        currentUpdatedChannel: null,
        currentUpdatedTarget: null,
        currentUpdatedOwner: null,
    }),
    computed: {
        ...mapState("itemDetail", ["item", "fieldsCurrentlyUpdating", "inactiveMentionGroups"]),
        ...mapState("choices", ["choices"]),
        labels() {
            let labels = {
                project: this.$t("project"),
                owners: this.$t("owners"),
                channels: this.$t("channels"),
                targets: this.$t("targets"),
                tags: this.$t("tags"),
            }
            if (this.item.itemType) {
                _.forEach(this.item.itemType.metadata_schema, (schema, fieldName) => {
                    if (schema.label) {
                        labels[fieldName] = schema.label
                    }
                })
            }
            return labels
        },
        sortedChannels() {
            return sortByAlphaString(this.item.channels, (channel) => channel.name)
        },
        pickedChannels() {
            return this.item.channels.map(
                (channel) =>
                    new PickedChannel(
                        channel.id,
                        getItemPathInHierarchy(channel.hierarchy, this.item.id),
                    ),
            )
        },
        sortedTargets() {
            return sortByAlphaString(this.item.targets, (target) => target.name)
        },
        sortedOwners() {
            return sortByAlphaString(this.item.owners, (owner) => owner.username)
        },
        projectDescriptionHtml() {
            return richTextSchema.HTMLFromJSON(this.item.project.description)
        },
    },
    methods: {
        ...mapActions("itemDetail", [
            "receiveItem",
            "toggleIsPrivate",
            "partialUpdateItem",
            "closePanel",
        ]),
        ...mapActions("itemDetail/activityFeed", ["fetchActivities"]),
        onProjectPicked(project) {
            // Remove the picked project if it is already selected
            let projectId = project.id == this.item.project_id ? null : project.id
            this.closeOffPanel("projectPicker")
            this.partialUpdateItem({
                project_id: projectId,
            })
        },
        onChannelPicked(pickedChannels) {
            this.partialUpdateItem({
                channels_id: pickedChannels.map((pc) => pc.channelId),
                picked_channels: pickedChannels
            })
        },
        onTargetPicked(targets_id) {
            this.partialUpdateItem({ targets_id })
        },
        onOwnerPicked(owners_id) {
            this.partialUpdateItem({ owners_id })
        },
        onTagsInput(tags) {
            this.partialUpdateItem({
                tags_id: tags.map((tag) => tag.id),
            })
        },
        removeChannel(channel) {
            this.currentUpdatedChannel = channel.id
            this.partialUpdateItem({
                channels_id: _.pull(this.item.channels_id, channel.id),
            }).then(() => {
                this.currentUpdatedChannel = null
            })
        },
        removeTarget(target) {
            this.currentUpdatedTarget = target.id
            this.partialUpdateItem({
                targets_id: _.pull(this.item.targets_id, target.id),
            }).then(() => {
                this.currentUpdatedTarget = null
            })
        },
        removeOwner(owner) {
            this.currentUpdatedOwner = owner.id
            this.partialUpdateItem({
                owners_id: _.pull(this.item.owners_id, owner.id),
            }).then(() => {
                this.currentUpdatedOwner = null
            })
        },
        getHierarchyPath(projel) {
            let path = getItemPathInHierarchy(projel.hierarchy, this.item.id)
            return path ? path.join("/") : ""
        },
        getChannelDescriptionHtml(channel) {
            return richTextSchema.HTMLFromJSON(channel.description)
        },
        onStateSaved(item) {
            // Update the item with the new state
            this.receiveItem(item)
            // Reload the activity list
            this.fetchActivities()
        },
    },
    i18n: {
        messages: {
            fr: {
                contentType: "Type de contenu",
                itemsInProject: "Contenus dans le projet",
                noTag: "Aucun tag",
            },
            en: {
                contentType: "Content type",
                itemsInProject: "Contents in project",
                noTag: "No tag",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.DrawerInformations {
    .Metadata {
        @apply flex items-center w-full justify-end;
    }

    .MetadataBlock {
        @apply flex flex-col my-6 bg-white border border-gray-200 p-4 rounded;
    }

    .MetadataBlock__Header {
        @apply flex items-center font-medium w-full mb-1;
    }
    .MetadataBlock__Icon {
        @apply w-4 mr-2 flex-shrink-0;
    }
    .MetadataBlock__Settings {
        @apply ml-auto text-gray-600;
        &:hover {
            @apply text-blue-600;
        }
    }

    .MetadataBlock__empty {
        @apply text-gray-600 text-sm font-medium;
    }

    .Metadata__Name {
        @apply flex-shrink-0 flex items-center leading-tight text-sm font-medium mr-1;

        &:hover {
            @apply underline;
        }
    }
    .Metadata__HierarchyPath {
        @apply text-xs text-gray-500 truncate flex-grow;
    }

    .Metadata__Details {
        @apply pl-2 border-l-2 border-gray-200;
    }
}
</style>
