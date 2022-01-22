<template>
<div class="ProjelDetailTabs tabs flex flex-grow">
    <router-link
        class="tab"
        active-class="is-active"
        to="informations"
    >
        <Icon name="Info" />
        <span class="tabLabel">{{ $t("infos") }}</span>
    </router-link>

    <router-link
        class="tab"
        active-class="is-active"
        to="contents"
    >
        <Icon name="Item" />
        <span class="tabLabel">{{ $t("contents") }}</span>
        <span class="tabBadge">{{ itemsCount }}</span>
    </router-link>

    <router-link
        v-if="isChannelRoute"
        class="tab"
        active-class="is-active"
        to="hierarchy"
    >
        <Icon
            class="stroke-none fill-current"
            name="Hierarchy"
        />
        <span class="tabLabel">{{ $t("treeView") }}</span>
    </router-link>

    <router-link
        v-if="isProjectRoute"
        class="tab"
        active-class="is-active"
        to="activity"
    >
        <Icon name="Comment" />
        <span class="tabLabel">{{ $t("comments") }}</span>
        <span class="tabBadge">{{ commentsCount }}</span>
    </router-link>

    <router-link
        v-if="isProjectRoute"
        class="tab"
        active-class="is-active"
        to="tasks"
    >
        <Icon name="Check" />
        <span class="tabLabel">{{ $t("tasks") }}</span>
        <span class="tabBadge">{{ linkedTasksTodo.length }}</span>
    </router-link>

    <router-link
        v-if="isProjectRoute"
        class="tab"
        active-class="is-active"
        to="assets"
    >
        <Icon name="Asset" />
        <span class="tabLabel">{{ $t("linkedAssets") }}</span>
        <span class="tabBadge">{{ linkedAssets.length }}</span>
    </router-link>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ProjelDetailTabs",
    mixins: [PilotMixin],
    computed: {
        ...mapState("projelDetail", ["projel", "itemsCount"]),
        ...mapState("projelDetail/linkedAssets", ["linkedAssets"]),
        ...mapGetters("projelDetail/linkedTasks", ["linkedTasksTodo"]),
        ...mapGetters("projelDetail/activityFeed", ["commentsCount"]),
        ...mapGetters("projelDetail", ["isChannelRoute", "isProjectRoute"]),
    },
}
</script>
