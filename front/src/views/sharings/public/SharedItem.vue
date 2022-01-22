<template>
<!-- This div around <ContentFormContainer> is REQUIRED to position correctly the sticky menubar
Please don't remove it -->
<div class="SharedItem">
    <ContentFormContainer
        v-if="item.id"
        :editable="sharing.is_editable"
    >
        <SharedItemEdition v-if="sharing.is_editable && !item.frozen" />
        <ItemContentReadOnly
            v-else
            :itemReadOnly="itemReadOnly"
        />
    </ContentFormContainer>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import SharedItemHeader from "./SharedItemHeader.vue"
import SharedItemEdition from "./SharedItemEdition.vue"
import ItemContentReadOnly from "@views/items/contentForm/ItemContentReadOnly"
import ContentFormContainer from "@views/items/contentForm/ContentFormContainer"

export default {
    name: "SharedItem",
    mixins: [PilotMixin],
    components: {
        SharedItemHeader,
        ItemContentReadOnly,
        SharedItemEdition,
        ContentFormContainer,
    },
    computed: {
        ...mapState(["sharing"]),
        ...mapState("sharedItem", ["item", "itemReadOnly"]),
    },
    methods: {
        ...mapActions("sharedItem", ["fetchSharedItem"]),
    },
    created() {
        this.fetchSharedItem()
    },
}
</script>
