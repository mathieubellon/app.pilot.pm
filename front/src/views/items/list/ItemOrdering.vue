<template>
<OrderingSelector
    :context="context"
    defaultOrdering="-updated_at"
    :orderings="orderings"
    :value="value"
    @orderingChange="$emit('orderingChange', $event)"
/>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import OrderingSelector from "@views/bigFilter/OrderingSelector"

export default {
    name: "ItemOrdering",
    mixins: [PilotMixin],
    components: {
        OrderingSelector,
    },
    props: {
        value: String,
    },
    computed: {
        ...mapGetters("projelDetail", ["isChannelRoute", "isProjectRoute"]),
        orderings() {
            let orderings = [
                { value: "updated_at", label: this.$t("sortByUpdateDateAsc") },
                { value: "-updated_at", label: this.$t("sortByUpdateDateDesc") },
                { value: "created_at", label: this.$t("sortByCreatedDateAsc") },
                { value: "-created_at", label: this.$t("sortByCreatedDateDesc") },
                { value: "publication_dt", label: this.$t("sortByPublicationDateAsc") },
                { value: "-publication_dt", label: this.$t("sortByPublicationDateDesc") },
                { value: "id", label: this.$t("sortById") },
                { value: "item_title", label: this.$t("sortByTitleAsc") },
                { value: "-item_title", label: this.$t("sortByTitleDesc") },
                { value: "project__name", label: this.$t("sortByProjectNameAsc") },
                { value: "-project__name", label: this.$t("sortByProjectNameDesc") },
                { value: "channels__name", label: this.$t("sortByChannelNameAsc") },
                { value: "-channels__name", label: this.$t("sortByChannelNameDesc") },
                { value: "workflow_state__order", label: this.$t("sortByWorkflowOrderAsc") },
                { value: "-workflow_state__order", label: this.$t("sortByWorkflowOrderDesc") },
            ]
            if (this.context == "project") {
                orderings = orderings.filter(
                    (ordering) => !ordering.value.includes("project__name"),
                )
            }
            if (this.context == "channel") {
                orderings = orderings.filter(
                    (ordering) => !ordering.value.includes("channels__name"),
                )
            }
            return orderings
        },
        context() {
            if (this.isChannelRoute) {
                return "channel"
            }
            if (this.isProjectRoute) {
                return "project"
            }
            return null
        },
    },
    i18n: {
        messages: {
            fr: {
                sortByChannelNameAsc: "Canal A->Z",
                sortByChannelNameDesc: "Canal Z->A",
                sortByCreatedDateAsc: "Date de création la plus ancienne en premier",
                sortByCreatedDateDesc: "Date de création la plus récente en premier",
                sortById: "Id",
                sortByProjectNameAsc: "Projet A->Z",
                sortByProjectNameDesc: "Projet Z->A",
                sortByPublicationDateAsc: "Date de publication la plus ancienne en premier",
                sortByPublicationDateDesc: "Date de publication la plus récente en premier",
                sortByTitleAsc: "Titre A->Z",
                sortByTitleDesc: "Titre Z->A",
                sortByUpdateDateAsc: "Date de mise à jour la plus ancienne en premier",
                sortByUpdateDateDesc: "Date de mise à jour la plus récente en premier",
                sortByWorkflowOrderAsc: "Statut Ascendant",
                sortByWorkflowOrderDesc: "Statut Descendant",
            },
            en: {
                sortByChannelNameAsc: "Channel A->Z",
                sortByChannelNameDesc: "Channel Z->A",
                sortByCreatedDateAsc: "Creation date, oldest first",
                sortByCreatedDateDesc: "Creation date, newest first",
                sortById: "Id",
                sortByProjectNameAsc: "Project A->Z",
                sortByProjectNameDesc: "Project Z->A",
                sortByPublicationDateAsc: "Publication date, oldest first",
                sortByPublicationDateDesc: "Publication date, newest first",
                sortByTitleAsc: "Title A->Z",
                sortByTitleDesc: "Title Z->A",
                sortByUpdateDateAsc: "Updated date, oldest first",
                sortByUpdateDateDesc: "Updated date, newest first",
                sortByWorkflowOrderAsc: "Status Ascending",
                sortByWorkflowOrderDesc: "Status Descending",
            },
        },
    },
}
</script>
