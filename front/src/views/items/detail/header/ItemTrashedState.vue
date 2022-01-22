<template>
<SmartButtonSpinner
    v-if="item.in_trash"
    name="itemRestoreFromTrash"
    @click.prevent="restoreFromTrash()"
>
    {{ $t("restore") }}
</SmartButtonSpinner>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ItemTrashedState",
    mixins: [PilotMixin],
    computed: {
        ...mapState("itemDetail", ["item"]),
    },
    methods: {
        ...mapActions("itemDetail", ["restoreFromTrash"]),
    },
    i18n: {
        messages: {
            fr: {
                restore: "Restaurer ce contenu",
                trash: "Corbeille",
            },
            en: {
                restore: "Restore this content",
                trash: "Trash",
            },
        },
    },
}
</script>
