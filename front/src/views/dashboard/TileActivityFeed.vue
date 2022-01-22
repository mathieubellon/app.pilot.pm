<template>
<div class="DashboardTile">
    <div class="DashboardTile__header">
        <span>{{ tile.title }}</span>

        <Popper triggerElementName="PopperRef">
            <template #triggerElement>
                <button ref="PopperRef">
                    <Icon name="MenuDotsHorizontal" />
                </button>
            </template>

            <template #content>
                <div class="w-40">
                    <MenuItemWithConfirm
                        iconName="Trash"
                        :isRed="true"
                        :label="$t('remove')"
                        @confirmed="removeTileFromUserTiles(tileIndex)"
                    />
                </div>
            </template>
        </Popper>
    </div>
    <div class="DashboardTile__body">
        <ActivityFeed namespace="dashboard" />
    </div>
</div>
</template>

<script>
import { mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"
import TileMixin from "./TileMixin.vue"
import MenuItemWithConfirm from "@components/MenuItemWithConfirm"
import ActivityFeed from "@views/activity/ActivityFeed.vue"

export default {
    name: "TileActivityFeed",
    mixins: [TileMixin, PilotMixin],
    components: {
        ActivityFeed,
        MenuItemWithConfirm,
    },
    methods: {
        ...mapMutations("dashboard/activityFeed", ["initActivityFeedStore"]),
        ...mapActions("dashboard/activityFeed", ["fetchActivities"]),
    },
    mounted() {
        this.initActivityFeedStore({
            queryParams: this.tile.queryParams,
        })
        this.fetchActivities()
    },
}
</script>
