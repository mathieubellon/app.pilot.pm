<template>
<div class="ProjelDetailSideBar">
    <transition
        enter-active-class="animated fadeIn"
        leave-active-class="animated fadeOut"
        mode="out-in"
    >
        <div
            v-if="!projel.id"
            class="bg-white border border-gray-200 rounded px-3 py-5"
        >
            <BarLoader
                :color="colors.grey500"
                :width="100"
                widthUnit="%"
            />
        </div>

        <div v-else>
            <div
                v-if="isChannelRoute"
                class="ProjelDetailSideBar__panel"
            >
                <div class="ProjelDetailSideBar__panelHeader">
                    <div class="ProjelDetailSideBar__panelTitle">{{ $t("type") }}</div>

                    <LabelSelect
                        :multiple="false"
                        placement="right"
                        targetType="channel_type"
                        triggerElementName="PopperRef"
                        :value="projel.type"
                        @input="onChannelTypeInput"
                    >
                        <template #triggerElement>
                            <a
                                class="ProjelDetailSideBar__panelHeaderLink button is-small"
                                ref="PopperRef"
                            >
                                {{ $t("edit") }}
                            </a>
                        </template>
                    </LabelSelect>
                </div>

                <Spinner v-if="fieldsCurrentlyUpdating.type_id" />
                <template v-else>
                    <Label
                        v-if="projel.type"
                        :goToListOnClick="true"
                        :label="projel.type"
                    />
                    <template v-else>{{ $t("noChannelType") }}</template>
                </template>
            </div>

            <div
                v-if="isProjectRoute"
                class="ProjelDetailSideBar__panel"
            >
                <div class="ProjelDetailSideBar__panelHeader">
                    <div class="ProjelDetailSideBar__panelTitle">{{ $t("priority") }}</div>
                    <LabelSelect
                        :multiple="false"
                        placement="right"
                        targetType="project_priority"
                        triggerElementName="PriorityPopper"
                        :value="projel.priority"
                        @input="onPriorityInput"
                    >
                        <template #triggerElement>
                            <a
                                class="ProjelDetailSideBar__panelHeaderLink button is-small"
                                ref="PriorityPopper"
                            >
                                {{ $t("edit") }}
                            </a>
                        </template>
                    </LabelSelect>
                </div>

                <Spinner v-if="fieldsCurrentlyUpdating.priority_id" />
                <template v-else>
                    <Label
                        v-if="projel.priority"
                        class="text-base"
                        :goToListOnClick="true"
                        :label="projel.priority"
                    />
                    <div v-else>{{ $t("noPriority") }}</div>
                </template>
            </div>

            <div
                v-if="isProjectRoute"
                class="ProjelDetailSideBar__panel"
            >
                <div class="ProjelDetailSideBar__panelHeader">
                    <div class="ProjelDetailSideBar__panelTitle">{{ $t("dates") }}</div>
                </div>

                <table>
                    <tr>
                        <td class="text-sm font-medium text-gray-700">{{ $t("start") }}</td>
                        <td class="pl-3">
                            <DatePickerPopper
                                :formatWithoutTime="true"
                                triggerElementName="StartDatePopper"
                                :value="projel.start"
                                @input="onStartInput"
                            >
                                <template #triggerElement>
                                    <div ref="StartDatePopper">
                                        <Spinner v-if="fieldsCurrentlyUpdating.start" />
                                        <button
                                            v-else
                                            class="menu-item"
                                        >
                                            <span
                                                v-if="projel.start"
                                                class=""
                                            >
                                                {{ projel.start | dateFormat("DD MMMM YYYY") }}
                                            </span>
                                            <span
                                                v-else
                                                class="text-gray-600"
                                            >
                                                {{ $t("add") }}
                                            </span>
                                        </button>
                                    </div>
                                </template>
                            </DatePickerPopper>
                        </td>
                    </tr>
                    <tr>
                        <td class="text-sm font-medium text-gray-700">{{ $t("end") }}</td>
                        <td class="pl-3">
                            <DatePickerPopper
                                :formatWithoutTime="true"
                                triggerElementName="EndDatePopper"
                                :value="projel.end"
                                @input="onEndInput"
                            >
                                <template #triggerElement>
                                    <div ref="EndDatePopper">
                                        <Spinner v-if="fieldsCurrentlyUpdating.end" />
                                        <button
                                            v-else
                                            class="menu-item"
                                        >
                                            <span
                                                v-if="projel.end"
                                                class=""
                                            >
                                                {{ projel.end | dateFormat("DD MMMM YYYY") }}
                                            </span>
                                            <span
                                                v-else
                                                class="text-gray-600"
                                            >
                                                {{ $t("add") }}
                                            </span>
                                        </button>
                                    </div>
                                </template>
                            </DatePickerPopper>
                        </td>
                    </tr>
                </table>
            </div>

            <div class="ProjelDetailSideBar__panel">
                <div class="ProjelDetailSideBar__panelHeader">
                    <div class="ProjelDetailSideBar__panelTitle">{{ $t("owners") }}</div>
                    <a
                        class="ProjelDetailSideBar__panelHeaderLink button is-small"
                        @click="openOffPanel('ownerPicker')"
                    >
                        {{ $t("edit") }}
                    </a>
                </div>

                <Spinner v-if="fieldsCurrentlyUpdating.owners_id" />
                <div v-else-if="projel.owners.length > 0">
                    <div
                        v-for="owner in sortedOwners"
                        class="ProjelDetailSideBar__panelUserElement"
                    >
                        <UserDisplay
                            :user="owner"
                            :withAvatar="true"
                        />
                        <a @click.stop.prevent="removeOwner(owner)">
                            <Icon
                                class="text-gray-500 w-4"
                                name="Close"
                                v-tooltip.right="$t('remove')"
                            />
                        </a>
                    </div>
                </div>
                <div v-else>{{ $t("noOwner") }}</div>

                <OffPanel name="ownerPicker">
                    <div slot="offPanelTitle">{{ $t("selectOwners") }}</div>
                    <UserPicker
                        slot="offPanelBody"
                        :loading="fieldsCurrentlyUpdating.owners_id"
                        :multiple="true"
                        :pickedUsersId="projel.owners_id"
                        :users="choices.users"
                        @pick="onOwnerPicked"
                    />
                </OffPanel>
            </div>

            <div
                v-if="isProjectRoute"
                class="ProjelDetailSideBar__panel"
            >
                <div class="ProjelDetailSideBar__panelHeader">
                    <div class="ProjelDetailSideBar__panelTitle">{{ $t("members") }}</div>
                    <a
                        class="ProjelDetailSideBar__panelHeaderLink button is-small"
                        @click="openOffPanel('memberPicker')"
                    >
                        {{ $t("edit") }}
                    </a>
                </div>

                <Spinner v-if="fieldsCurrentlyUpdating.members_id" />
                <div v-else-if="projel.members.length > 0">
                    <div
                        v-for="member in sortedMembers"
                        class="ProjelDetailSideBar__panelUserElement"
                    >
                        <UserDisplay
                            :user="member"
                            :withAvatar="true"
                        />
                        <a @click.stop.prevent="removeMember(member)">
                            <Icon
                                class="text-gray-500 w-4"
                                name="Close"
                                v-tooltip.right="$t('remove')"
                            />
                        </a>
                    </div>
                </div>
                <div v-else>{{ $t("noMember") }}</div>

                <OffPanel name="memberPicker">
                    <div slot="offPanelTitle">{{ $t("selectMembers") }}</div>
                    <UserPicker
                        slot="offPanelBody"
                        :loading="fieldsCurrentlyUpdating.members_id"
                        :multiple="true"
                        :pickedUsersId="projel.members_id"
                        :users="choices.users"
                        @pick="onMemberPicked"
                    />
                </OffPanel>
            </div>

            <div
                v-if="isProjectRoute"
                class="ProjelDetailSideBar__panel"
            >
                <div class="ProjelDetailSideBar__panelHeader">
                    <div class="ProjelDetailSideBar__panelTitle">{{ $t("category") }}</div>

                    <LabelSelect
                        :multiple="false"
                        placement="right"
                        targetType="project_category"
                        triggerElementName="CategoryPopper"
                        :value="projel.category"
                        @input="onCategoryInput"
                    >
                        <template #triggerElement>
                            <a
                                class="ProjelDetailSideBar__panelHeaderLink button is-small"
                                ref="CategoryPopper"
                            >
                                {{ $t("edit") }}
                            </a>
                        </template>
                    </LabelSelect>
                </div>

                <Spinner v-if="fieldsCurrentlyUpdating.category_id" />
                <template v-else>
                    <Label
                        v-if="projel.category"
                        :goToListOnClick="true"
                        :label="projel.category"
                    />
                    <template v-else>{{ $t("noLabel") }}</template>
                </template>
            </div>

            <div
                v-if="isProjectRoute"
                class="ProjelDetailSideBar__panel"
            >
                <div class="ProjelDetailSideBar__panelHeader">
                    <div class="ProjelDetailSideBar__panelTitle">{{ $t("channels") }}</div>
                    <a
                        class="ProjelDetailSideBar__panelHeaderLink button is-small"
                        @click="openOffPanel('channelPicker')"
                    >
                        {{ $t("edit") }}
                    </a>
                </div>

                <Spinner v-if="fieldsCurrentlyUpdating.channels_id" />
                <div v-else-if="projel.channels.length > 0">
                    <div v-for="channel in sortedChannels">
                        <SmartLink :to="channel.url">{{ channel.name }}</SmartLink>
                    </div>
                </div>
                <div v-else>{{ $t("noChannel") }}</div>

                <OffPanel name="channelPicker">
                    <div slot="offPanelTitle">{{ $t("selectChannels") }}</div>
                    <ChannelPicker
                        slot="offPanelBody"
                        :channels="choices.channels"
                        :loading="fieldsCurrentlyUpdating.channels_id"
                        :pickedChannels="pickedChannels"
                        :withHierarchy="false"
                        @pick="onChannelPicked"
                    />
                </OffPanel>
            </div>

            <div
                v-if="isProjectRoute"
                class="ProjelDetailSideBar__panel"
            >
                <div class="ProjelDetailSideBar__panelHeader">
                    <div class="ProjelDetailSideBar__panelTitle">{{ $t("targets") }}</div>
                    <a
                        class="ProjelDetailSideBar__panelHeaderLink button is-small"
                        @click="openOffPanel('targetPicker')"
                    >
                        {{ $t("edit") }}
                    </a>
                </div>

                <Spinner v-if="fieldsCurrentlyUpdating.targets_id" />
                <div v-else-if="projel.targets.length > 0">
                    <div v-for="target in sortedTargets">
                        {{ target.name }}
                    </div>
                </div>
                <div v-else>{{ $t("noTarget") }}</div>

                <OffPanel name="targetPicker">
                    <div slot="offPanelTitle">{{ $t("selectTarget") }}</div>
                    <TargetPicker
                        slot="offPanelBody"
                        :loading="fieldsCurrentlyUpdating.targets_id"
                        :multiple="true"
                        :pickedTargetsId="projel.targets_id"
                        :targets="choices.targets"
                        @pick="onTargetPicked"
                    />
                </OffPanel>
            </div>

            <div
                v-if="isProjectRoute"
                class="ProjelDetailSideBar__panel"
            >
                <div class="ProjelDetailSideBar__panelHeader">
                    <div class="ProjelDetailSideBar__panelTitle">{{ $t("tags") }}</div>

                    <LabelSelect
                        :isUpdating="fieldsCurrentlyUpdating.tags_id"
                        :multiple="true"
                        :sortable="false"
                        targetType="project_tags"
                        triggerElementName="TagPopper"
                        :value="projel.tags"
                        @input="onTagsInput"
                    >
                        <template #triggerElement>
                            <a
                                class="ProjelDetailSideBar__panelHeaderLink button is-small"
                                ref="TagPopper"
                            >
                                {{ $t("edit") }}
                            </a>
                        </template>
                    </LabelSelect>
                </div>

                <Spinner v-if="fieldsCurrentlyUpdating.tags_id" />
                <template v-else>
                    <div
                        v-if="projel.tags.length > 0"
                        class="ProjelDetailSideBar__tags"
                    >
                        <Label
                            v-for="tag in projel.tags"
                            :goToListOnClick="true"
                            :key="tag.id"
                            :label="tag"
                        />
                    </div>
                    <template v-else>{{ $t("noTags") }}</template>
                </template>
            </div>

            <div class="ProjelDetailSideBar__panel">
                <div class="ProjelDetailSideBar__panelHeader">
                    <div class="ProjelDetailSideBar__panelTitle">{{ $t("informations") }}</div>
                </div>
                <div class="text-sm font-medium text-gray-700">{{ $t("createdBy") }}</div>
                <div class="mb-3">
                    <a v-if="projel.created_by_external_email">
                        {{ projel.created_by_external_email }}
                    </a>
                    <UserDisplay
                        v-else
                        :user="projel.created_by"
                    />
                </div>
                <div class="text-sm font-medium text-gray-700">{{ $t("updatedBy") }}</div>
                <div>
                    <UserDisplay
                        v-if="projel.updated_by"
                        :user="projel.updated_by"
                    />
                </div>
            </div>
        </div>
    </transition>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"

import Label from "@views/labels/Label.vue"
import LabelSelect from "@views/labels/LabelSelect.vue"
import ChannelPicker from "@components/picker/ChannelPicker.vue"
import { PickedChannel } from "@components/picker/ChannelPickerElement.vue"
import TargetPicker from "@components/picker/TargetPicker.vue"
import UserPicker from "@components/picker/UserPicker.vue"

export default {
    name: "ProjelDetailSideBar",
    mixins: [PilotMixin],
    components: {
        Label,
        LabelSelect,
        ChannelPicker,
        TargetPicker,
        UserPicker,
    },

    computed: {
        ...mapState("projelDetail", ["projel", "fieldsCurrentlyUpdating"]),
        ...mapState("choices", ["choices"]),
        ...mapGetters("projelDetail", ["isChannelRoute", "isProjectRoute"]),
        sortedTargets() {
            if (!this.projel.targets) {
                return []
            }
            return sortByAlphaString(this.projel.targets, (target) => target.name)
        },
        sortedMembers() {
            if (!this.projel.members) {
                return []
            }
            return sortByAlphaString(this.projel.members, (member) => member.username)
        },
        sortedOwners() {
            if (!this.projel.owners) {
                return []
            }
            return sortByAlphaString(this.projel.owners, (owner) => owner.username)
        },
        sortedChannels() {
            if (!this.projel.channels) {
                return []
            }
            return sortByAlphaString(this.projel.channels, (channel) => channel.name)
        },
        pickedChannels() {
            return this.projel.channels.map((channel) => new PickedChannel(channel.id))
        },
    },
    methods: {
        ...mapActions("projelDetail", ["partialUpdateProjel"]),
        onChannelTypeInput(type) {
            this.partialUpdateProjel({
                type_id: type ? type.id : null,
            })
        },
        onPriorityInput(priority) {
            this.partialUpdateProjel({
                priority_id: priority ? priority.id : null,
            })
        },
        onStartInput(start) {
            this.partialUpdateProjel({ start })
        },
        onEndInput(end) {
            this.partialUpdateProjel({ end })
        },
        onMemberPicked(members_id) {
            this.partialUpdateProjel({ members_id })
        },
        onOwnerPicked(owners_id) {
            this.partialUpdateProjel({ owners_id })
        },
        removeMember(member) {
            this.partialUpdateProjel({
                members_id: _.pull(this.projel.members_id, member.id),
            })
        },
        removeOwner(owner) {
            this.partialUpdateProjel({
                owners_id: _.pull(this.projel.owners_id, owner.id),
            })
        },
        onCategoryInput(category) {
            this.partialUpdateProjel({
                category_id: category ? category.id : null,
            })
        },
        onChannelPicked(pickedChannels) {
            this.partialUpdateProjel({
                channels_id: pickedChannels.map((pc) => pc.channelId),
            })
        },
        onTargetPicked(targets_id) {
            this.partialUpdateProjel({ targets_id })
        },
        onTagsInput(tags) {
            this.partialUpdateProjel({
                tags_id: tags.map((tag) => tag.id),
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                dates: "Dates",
                category: "Catégorie",
                noChannelType: "Aucun type",
                noChannel: "Aucun canal associé au projet",
                noLabel: "Aucune",
                noMember: "Aucun membre",
                noOwner: "Aucun responsable",
                noPriority: "Aucune priorité",
                noTags: "Aucun tag",
                noTarget: "Aucune cible associée au projet",
            },
            en: {
                dates: "Dates",
                category: "Category",
                noChannelType: "No type",
                noChannel: "No channel associated to the project",
                noLabel: "None",
                noMember: "No member",
                noOwner: "No owner",
                noPriority: "No priority",
                noTags: "No tag",
                noTarget: "No target associated to the project",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/include_media.scss";

.ProjelDetailSideBar {
    @apply flex flex-col;
}

.ProjelDetailSideBar__panel {
    @apply flex-col bg-white border border-gray-200 rounded p-3 mb-2;

    overflow: hidden;
    text-overflow: ellipsis;

    &:hover {
        .ProjelDetailSideBar__panelHeaderLink {
            visibility: visible;
        }
    }
}

.ProjelDetailSideBar__panelHeader {
    @apply mb-1 flex flex-grow justify-between items-center w-full;

    .ProjelDetailSideBar__panelTitle {
        @apply text-sm font-bold text-gray-800;
    }
}

.ProjelDetailSideBar__panelHeaderLink {
    visibility: hidden;
}

.ProjelDetailSideBar__panelUserElement {
    @apply flex items-center justify-between bg-gray-50 p-1 mb-1 rounded;
}

.ProjelDetailSideBar__tags {
    display: flex;
    flex-direction: row;
    flex-flow: wrap;

    .Label {
        margin-right: 5px;
        margin-bottom: 5px;
    }
}
</style>
