<template>
<div class="h-screen overflow-y-hidden flex flex-col">
    <div
        v-if="sharing.deactivated"
        class="hero-container"
    >
        <div class="hero-panel text-center">
            {{ $t("sharingDeactivated") }}
        </div>
    </div>

    <template v-else>
        <keep-alive include="SharingHeader">
            <router-view
                class="SharingApp__header"
                name="header"
            />
        </keep-alive>

        <keep-alive include="Sharing">
            <!-- We need the app-body id for the scroll position remembering feature -->
            <router-view
                id="app-body"
                class="SharingApp__body"
                name="body"
            />
        </keep-alive>
    </template>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { QueryParamSerializer } from "@js/queryString"
import {
    getSharedItemApiSource,
    getSharedItemCalendarApiSource,
    getSharedProjectCalendarApiSource,
} from "@js/apiSource"
import PilotMixin from "@components/PilotMixin"
import { SharingType } from "@/store/PublicSharingStore"

const listTypes = [SharingType.PROJECT, SharingType.CHANNEL, SharingType.LIST]

export default {
    name: "PublicSharingApp",
    mixins: [PilotMixin],
    data: () => ({
        SharingType,
    }),
    computed: {
        ...mapState(["sharing"]),
    },
    methods: {
        ...mapMutations(["setSharing"]),
        ...mapMutations("itemList", ["setQueryParamsFromQueryString"]),

        ...mapActions("calendar", ["fetchCalendarEvents"]),
        ...mapActions("itemList", ["fetchItemList"]),
    },
    created() {
        // Rendering context, coming from server-side.
        // We need to clone it to prevent memory leak incurred by a top-level reactive object.
        this.setSharing(_.cloneDeep(window.sharingContext.sharing))
        let isSlidingCalendar = _.get(this.sharing, "saved_filter.is_sliding_calendar", true)

        if (this.sharing.type == SharingType.CALENDAR) {
            let itemsApiSource = getSharedItemCalendarApiSource(this.sharing.token)

            let serializer = new QueryParamSerializer(this.sharing.query_string)
            if (isSlidingCalendar) {
                serializer.removeParam("start")
                serializer.removeParam("end")
            }
            itemsApiSource.setQuery(serializer.params)

            this.$store.commit("calendar/setItemsApiSource", itemsApiSource)
            this.$store.commit(
                "calendar/setProjectsApiSource",
                getSharedProjectCalendarApiSource(this.sharing.token),
            )
        } else {
            let apiSource = getSharedItemApiSource(this.sharing.token)
            apiSource.setQueryString(this.sharing.query_string)

            this.$store.commit("itemList/setApiSource", apiSource)
        }

        // If this is a sharing for a single item, we can load the corresponding item right now
        if (this.sharing.type == SharingType.ITEM) {
            // Redirect directly to the item route
            if (this.$route.name == "sharing") {
                this.$router.push({
                    name: "sharedItem",
                    params: {
                        itemId: this.sharing.item_id,
                        token: this.sharing.token,
                    },
                })
            }
        }

        if (listTypes.includes(this.sharing.type)) {
            this.fetchItemList()
        } else {
            // With sliding calendars, the FullCalendar watcher on 'itemsApiSource.url' will fetch the events
            // after setting the dates
            if (!isSlidingCalendar) {
                this.fetchCalendarEvents()
            }
        }
    },
    i18n: {
        messages: {
            fr: {
                sharingDeactivated: "Ce partage a été désactivé, et n'est plus accessible.",
            },
            en: {
                sharingDeactivated:
                    "This sharing has been deactivated, and is not accessible anymore.",
            },
        },
    },
}
</script>

<style lang="scss">
.SharingApp__header {
    @apply flex flex-col justify-center bg-white border-b border-gray-200;

    min-height: 120px;
}

.SharingApp__body {
    @apply h-full flex justify-center items-start flex-grow overflow-y-auto;
}
</style>
