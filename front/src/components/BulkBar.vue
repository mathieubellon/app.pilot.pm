<template>
<div class="BulkBar">
    <div
        class="is-checkbox mr-4"
        @click="onCheckboxChange"
    >
        <input
            :checked="allSelectedForBulkAction"
            type="checkbox"
        />
    </div>

    <slot />

    <div class="mx-4 flex flex-grow items-center text-sm font-medium">
        <template v-if="wholeListSelected">
            {{ $tc("wholeListSelected", pagination.count) }}
        </template>
        <template v-else>
            {{ $tc("selectedCount", bulkActionSelectionAsList.length) }}
            {{ $tc("visibleCount", instances.length) }}
        </template>

        &nbsp;&bull;&nbsp;
        <a @click="deselectAllForBulkAction">{{ $t("deselectAll") }}</a>

        <template v-if="pagination && pagination.next && !wholeListSelected">
            &nbsp;&bull;&nbsp;
            <a @click="selectWholeListForBulkAction(queryParams)">
                {{ $tc("selectAll", pagination.count) }}
            </a>
        </template>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

export default {
    name: "BulkBar",
    props: {
        instances: Array,
        pagination: Object,
        queryParams: Object,
    },
    computed: {
        ...mapState("bulk", ["bulkActionSelection", "wholeListSelected"]),
        ...mapGetters("bulk", ["bulkActionSelectionAsList"]),
        allSelectedForBulkAction() {
            return (
                (this.instances.length > 0 &&
                    this.bulkActionSelectionAsList.length == this.instances.length) ||
                this.wholeListSelected
            )
        },
    },
    methods: {
        ...mapMutations("bulk", [
            "selectAllVisiblesForBulkAction",
            "selectWholeListForBulkAction",
            "deselectAllForBulkAction",
        ]),
        onCheckboxChange() {
            if (this.allSelectedForBulkAction) {
                this.deselectAllForBulkAction()
            } else {
                this.selectAllVisiblesForBulkAction(this.instances)
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                deselectAll: "Déselectionner",
                selectAll: "Sélectionner tous les {count} éléments",
                selectedCount: "1 sélectionné | {count} sélectionnés",
                visibleCount: "sur 1 visible | sur {count} visibles",
                wholeListSelected: "Tous les {count} sélectionnés",
            },
            en: {
                deselectAll: "Deselect",
                selectAll: "Select all the {count} items",
                selectedCount: "{count} selected",
                visibleCount: "on 1 visible | on {count} visibles",
                wholeListSelected: "All {count} selected",
            },
        },
    },
}
</script>
BulkBar

<style lang="scss">
.BulkBar {
    @apply flex justify-center items-center w-full;
}

.BulkBar__checkbox {
    @apply flex items-center content-center self-stretch border rounded border-transparent cursor-pointer mr-1 p-2;
    // Align with the checkboxes in the list,
    // because they have an additionnal 1px of border from the ListElement
    margin-left: 1px;

    &:hover {
        @apply bg-gray-100 border-gray-200;
    }
}
</style>
