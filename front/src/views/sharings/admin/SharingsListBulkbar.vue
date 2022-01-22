<template>
<transition
    v-if="anySelectedForBulkAction"
    enter-active-class="animated animated-500 fadeIn"
    leave-active-class="animated animated-500 fadeOut"
>
    <div class="SharingsListBulkbar">
        <BulkBar
            :instances="sharings"
            :pagination="pagination"
        >
            <div class="flex">
                <template v-if="!deactivationRequested">
                    <button
                        class="button is-red"
                        @click="deactivationRequested = true"
                    >
                        {{ $t("deactivate") }}
                    </button>
                </template>

                <div
                    v-else
                    class="flex py-2 px-4 bg-white rounded items-center border border-black"
                >
                    <span>
                        {{ $tc("areYouSureDeactivation", bulkActionSelectionAsList.length) }}
                    </span>
                    <SmartButtonSpinner
                        class="ml-2 mr-4 is-red"
                        name="bulkAction-deactivate"
                        :timeout="1500"
                        @click="bulkDeactivate"
                    >
                        {{ $t("confirmDeactivation") }}
                    </SmartButtonSpinner>
                    <button
                        class="button is-outlined"
                        @click="cancelDeactivation"
                    >
                        {{ $t("cancel") }}
                    </button>
                </div>
            </div>
        </BulkBar>
    </div>
</transition>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import urls from "@js/urls"
import PilotMixin from "@components/PilotMixin"

import BulkBar from "@components/BulkBar.vue"

export default {
    name: "SharingsListBulkbar",
    mixins: [PilotMixin],
    components: {
        BulkBar,
    },
    props: {
        sharings: Array,
        pagination: Object,
    },
    data: () => ({
        deactivationRequested: false,
    }),
    computed: {
        ...mapGetters("bulk", ["anySelectedForBulkAction", "bulkActionSelectionAsList"]),
    },
    methods: {
        ...mapMutations("bulk", ["deselectAllForBulkAction"]),
        ...mapActions("bulk", ["bulkAction"]),
        bulkDeactivate() {
            this.bulkAction({
                url: urls.sharingsBulkAction,
                action: "deactivate",
            }).then((ids) => {
                this.$emit("deactivated", ids)
            })
        },
        cancelDeactivation() {
            this.deactivationRequested = false
        },
    },
    i18n: {
        messages: {
            fr: {
                areYouSureDeactivation:
                    "Vous allez désactiver 1 partage, êtes vous sûr ? | Vous allez désactiver {count} partages, êtes vous sûr ? ",
                confirmDeactivation: "Ok, désactiver",
            },
            en: {
                areYouSureDeactivation:
                    "1 sharing will be deactivated, are you sure ? | {count} sharings will be deactivated, are you sure ?  ",
                confirmDeactivation: "Ok, deactivate",
            },
        },
    },
}
</script>

<style lang="scss">
.SharingsListBulkbar {
    @apply sticky top-0 bg-gray-50 py-2 border-b-2 border-gray-300;

    // Align exactly the checkbox with those into the list
    .BulkBar {
        margin-left: 26px;
    }
    margin-bottom: 10px;
}
</style>
