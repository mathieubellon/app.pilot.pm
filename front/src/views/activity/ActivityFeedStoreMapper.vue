<script>
import { mapInstanceState, mapInstanceGetters, mapInstanceActions } from "@js/lib/vuex-helpers"

const getNamespace = (vm) => `${vm.namespace}/activityFeed`

export default {
    name: "ActivityFeedStoreMapper",
    props: {
        namespace: String,
    },
    computed: {
        ...mapInstanceState(getNamespace, [
            "activities",
            "contentType",
            "objectId",
            "queryParams",
            "pagination",
        ]),
        ...mapInstanceGetters(getNamespace, ["isActivityListEmpty", "commentsCount"]),
    },
    methods: {
        ...mapInstanceActions(getNamespace, [
            "fetchActivities",
            "createComment",
            "editComment",
            "deleteComment",
        ]),
    },
}
</script>
