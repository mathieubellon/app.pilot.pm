<template>
<OffPanel
    name="itemBulkUpdate"
    @closed="onClosedUpdatePanel"
    @opened="onOpenUpdatePanel"
>
    <div slot="offPanelTitle">{{ $t("edit") }}</div>
    <div slot="offPanelBody">
        <Spinner v-if="!choicesReady" />

        <template v-else>
            <FormField
                v-if="!isProjectRoute"
                v-model="updateData.project_id"
                :schema="{
                    type: 'choice',
                    label: $t('project'),
                    choices: projectChoices,
                }"
            />

            <FormField
                v-model="updateData.owners_id"
                :schema="{
                    type: 'choice',
                    label: $t('owners'),
                    choices: usersChoices,
                    multiple: true,
                }"
            />

            <FormField
                v-if="!isChannelRoute"
                v-model="updateData.channels_id"
                :schema="{
                    type: 'choice',
                    label: $t('channels'),
                    choices: channelChoices,
                    multiple: true,
                }"
            />

            <FormField
                v-if="targetChoices.length > 0"
                v-model="updateData.targets_id"
                :schema="{
                    type: 'choice',
                    label: $t('targets'),
                    choices: targetChoices,
                    multiple: true,
                }"
            />

            <div class="form__field">
                <div class="form__field__label">{{ $t("tags") }}</div>

                <div class="ItemListBulkbar__tags">
                    <Label
                        v-for="tag in tags"
                        :goToListOnClick="false"
                        :key="tag.id"
                        :label="tag"
                    />
                </div>
                <br />
                <LabelSelect
                    :multiple="true"
                    placement="right"
                    :sortable="false"
                    targetType="item_tags"
                    triggerElementName="PopperRef"
                    :value="tags"
                    @input="onTagsInput"
                >
                    <template #triggerElement>
                        <a ref="PopperRef">{{ $t("selectTags") }}</a>
                    </template>
                </LabelSelect>
            </div>

            <SmartButtonSpinner
                name="bulkAction-update"
                @click="onUpdateConfirmed"
            >
                {{ $t("save") }}
            </SmartButtonSpinner>
        </template>
    </div>
</OffPanel>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { initialDataPromise } from "@js/bootstrap"
import PilotMixin from "@components/PilotMixin"
import ResponsiveMixin from "@components/ResponsiveMixin"

import Label from "@views/labels/Label.vue"
import LabelSelect from "@views/labels/LabelSelect.vue"

const EMPTY_UPDATE_MODEL = {
    project_id: null,
    owners_id: [],
    channels_id: [],
    targets_id: [],
    tags_id: [],
}

export default {
    name: "ItemBulkUpdatePanel",
    mixins: [PilotMixin, ResponsiveMixin],
    components: {
        Label,
        LabelSelect,
    },
    data: () => ({
        updateData: _.clone(EMPTY_UPDATE_MODEL),
        tags: [],
        choicesReady: true,
    }),
    computed: {
        ...mapGetters("choices", [
            "channelChoices",
            "projectChoices",
            "targetChoices",
            "usersChoices",
        ]),
        ...mapGetters("projelDetail", ["isChannelRoute", "isProjectRoute"]),
    },
    methods: {
        ...mapMutations("bulk", ["setSingleObjectSelection"]),
        ...mapMutations("offPanel", ["closeOffPanel"]),
        ...mapActions("itemActions", ["bulkUpdateItems"]),
        onOpenUpdatePanel() {
            this.updateData = _.clone(EMPTY_UPDATE_MODEL)
            this.tags = []

            this.choicesReady = false
            initialDataPromise.then(() => (this.choicesReady = true))
        },
        onClosedUpdatePanel() {
            this.setSingleObjectSelection(null)
        },
        onTagsInput(tags) {
            this.tags = tags
            this.updateData.tags_id = tags.map((tag) => tag.id)
        },
        onUpdateConfirmed() {
            this.bulkUpdateItems(
                _.omitBy(
                    this.updateData,
                    (data) => (_.isArray(data) && _.isEmpty(data)) || !data, // Keep only non-empty properties
                ),
            ).then((itemIds) => {
                setTimeout(() => this.closeOffPanel("itemBulkUpdate"), 1000)
            })
        },
    },
}
</script>

<style lang="scss">
.ItemListBulkbar__tags {
    display: flex;
    flex-direction: row;
    flex-flow: wrap;

    .Label {
        margin-right: 5px;
        margin-bottom: 5px;
    }
}
</style>
