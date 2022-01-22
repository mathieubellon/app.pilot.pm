<template>
<div class="tabs">
    <!--Info tab-->
    <a
        class="tab bg-transparent"
        :class="{ 'is-active': openedDrawer === 'infos' }"
        @click="openedDrawer != 'infos' ? openDrawer('infos') : closePanel()"
    >
        <Icon name="Info" />
        <span class="tabLabel">{{ $t("infos") }}</span>
    </a>

    <!--Publication date-->
    <DatePickerPopper
        :hideInput="true"
        :naiveTime="true"
        placement="bottom"
        triggerElementName="DatePickerRef"
        :value="publicationTask ? publicationTask.deadline : null"
        @input="onPublicationDateInput"
    >
        <template #message>
            <div class="flex items-center text-gray-700">
                {{ $t("publicationDate") }}
            </div>
            <div class="font-black">{{ item.publication_dt | dateFormat }}</div>
        </template>
        <template #triggerElement>
            <button
                class="tab is-small bg-transparent"
                ref="DatePickerRef"
            >
                <Icon
                    class="flex-shrink-0"
                    name="Calendar"
                />
                <BarLoader
                    v-if="fieldsCurrentlyUpdating.publication_dt"
                    :width="50"
                />
                <span
                    v-else-if="publicationTask && publicationTask.deadline"
                    class="tabLabel"
                >
                    {{ publicationTask.deadline | dateFormat }}
                </span>
                <span
                    v-else
                    class="tabLabel"
                >
                    {{ $t("noPublicationDate") }}
                </span>
            </button>
        </template>
    </DatePickerPopper>

    <!--Versions tab-->
    <a
        class="tab bg-transparent"
        :class="{ 'is-active': openedDrawer === 'history' }"
        @click="openedDrawer != 'history' ? openDrawer('history') : closePanel()"
    >
        <Icon name="Layers" />
        <span class="tabLabel">{{ $t("versions") }}</span>
        <span
            v-if="editSessions[0]"
            class="tabBadge"
        >
            {{ editSessions[0].version }}
        </span>
    </a>

    <!--Comments tab-->
    <a
        class="tab bg-transparent"
        :class="{ 'is-active': openedDrawer === 'activity' }"
        @click="openedDrawer != 'activity' ? openDrawer('activity') : closePanel()"
    >
        <Icon name="Comment" />
        <span class="tabLabel">{{ $t("comments") }}</span>
        <span class="tabBadge">{{ commentsCount }}</span>
    </a>

    <!--Tasks tab-->
    <a
        class="tab bg-transparent"
        :class="{ 'is-active': openedDrawer === 'tasks' }"
        @click="openedDrawer != 'tasks' ? openDrawer('tasks') : closePanel()"
    >
        <Icon name="Check" />
        <span class="tabLabel">{{ $t("tasks") }}</span>
        <span class="tabBadge">{{ linkedTasksTodo.length }}</span>
    </a>

    <!--Tab linked assets-->
    <a
        class="tab bg-transparent"
        :class="{ 'is-active': openedDrawer === 'assets' }"
        @click="openedDrawer != 'assets' ? openDrawer('assets') : closePanel()"
    >
        <Icon name="Asset" />
        <span class="tabLabel">{{ $t("linkedAssets") }}</span>
        <span class="tabBadge">{{ linkedAssets.length }}</span>
    </a>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ItemMiddleBarTabs",
    mixins: [PilotMixin],

    computed: {
        ...mapState("itemDetail", [
            "item",
            "openedDrawer",
            "editSessions",
            "linkedAssets",
            "fieldsCurrentlyUpdating",
        ]),
        ...mapState("itemDetail/linkedAssets", ["linkedAssets"]),
        ...mapGetters("itemDetail/linkedTasks", ["linkedTasksTodo", "publicationTask"]),
        ...mapGetters("itemDetail/activityFeed", ["commentsCount"]),
        ...mapGetters("itemDetail", ["inactiveMentionGroups"]),
    },
    methods: {
        ...mapActions("itemDetail", [
            "receiveItem",
            "partialUpdateItem",
            "openDrawer",
            "closePanel",
        ]),
        onPublicationDateInput(publicationDate) {
            this.partialUpdateItem({
                id: this.item.id,
                publication_dt: publicationDate,
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                noPublicationDate: "Date publication",
                history: "Historique",
                clickToSetPublicationDate: "Date de publication",
            },
            en: {
                noPublicationDate: "Publication date",
                history: "History",
                clickToSetPublicationDate: "Publication Date",
            },
        },
    },
}
</script>
