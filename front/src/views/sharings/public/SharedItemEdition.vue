<template>
<ItemContentForm />
</template>

<script>
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import realtime from "@js/realtime"
import PilotMixin from "@components/PilotMixin"

import ItemContentForm from "@views/items/detail/ItemContentForm"

export default {
    name: "SharedItemEdition",
    mixins: [PilotMixin],
    components: {
        ItemContentForm,
    },
    computed: {
        ...mapState(["sharing"]),
        ...mapState("itemContentForm", ["desynchronized", "isDisconnectedAfterInactivity"]),
        ...mapGetters("itemContentForm", ["anyPendingChanges"]),
        ...mapGetters("sharedItem", ["itemId"]),
    },
    methods: {
        ...mapMutations("itemContentForm", ["setMyRealtimeUser"]),
        ...mapActions("itemContentForm", ["initRealtime"]),
    },
    created() {
        let realtimeUser = {
            id: this.sharing.email,
            username: this.sharing.email,
        }
        // We need a realtime user right now to correctly init ItemContentRichEditor with the Collab module,
        // in its created hook.
        // We cannot wait for initRealtime to setMyRealtimeUser
        this.setMyRealtimeUser(realtimeUser)

        realtime.connect()
        realtime.connectPromise.then(() => {
            realtime.sharedItemAuth(this.sharing.token)

            this.initRealtime({
                itemId: this.itemId,
                realtimeUser,
            })
        })

        /***********************
         * Leave page with unsaved change
         ************************/
        // If there's pending changes when the page unload,
        // display an alert box preventing the user to leave page without confirmation
        this.onBeforeUnload = () => {
            if (
                this.anyPendingChanges &&
                !(this.desynchronized || this.isDisconnectedAfterInactivity)
            ) {
                return "Vos modifications n'ont pas été sauvegardées, elles seront perdues si vous quittez cette page"
            }
        }
        $(window).on("beforeunload", this.onBeforeUnload)
    },
    beforeDestroy() {
        $(window).off("beforeunload", this.onBeforeUnload)
    },
}
</script>
