<template>
<Popper
    triggerElementName="PopperRef"
    triggerType="click"
>
    <template #triggerElement>
        <button
            v-if="!hasDefaultValue"
            class="list-action-button border-red-500 text-red-700 bg-red-50"
            ref="PopperRef"
        >
            {{ $t("activeSort") }}
            <!-- The empty span is required to correctly align with flex display -->
            <span>
                <Icon
                    class="caret text-red-700"
                    name="ChevronDown"
                />
            </span>
        </button>

        <button
            v-else
            class="list-action-button m-0"
            ref="PopperRef"
        >
            {{ $t("sort") }}
            <!-- The empty span is required to correctly align with flex display -->
            <span>
                <Icon
                    class="caret"
                    name="ChevronDown"
                />
            </span>
        </button>
    </template>

    <template #content>
        <div class="OrderingSelector__list">
            <div
                v-if="context === 'project' || context === 'channel'"
                class="bg-blue-100 text-blue-800 text-sm p-2 rounded"
            >
                {{ $t("orderingIsShared") }}
            </div>

            <div
                v-if="!hasDefaultValue"
                class="bg-orange-100 text-orange-800 text-sm p-2 rounded mt-1"
            >
                {{ $t("warningListSorted") }}
            </div>
            <button
                v-if="!hasDefaultValue"
                class="button is-white is-small underline mb-2 text-blue-800"
                @click="setDefault()"
            >
                {{ $t("setdefault") }}
            </button>
            <div class="text-sm font-bold mt-2 pl-1">
                {{ $t("sortBy") }}
            </div>
            <a
                v-for="orderingOption in orderings"
                class="menu-item py-1"
                :class="{ 'bg-gray-200': orderingOption.value == value }"
                @click.prevent="emitChange(orderingOption.value)"
            >
                {{ orderingOption.label }}
            </a>
        </div>
    </template>
</Popper>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "OrderingSelector",
    mixins: [PilotMixin],
    props: {
        value: String,
        orderings: {
            type: Array,
            required: true,
        },
        defaultOrdering: {
            type: String,
        },
        // Can be null or 'project' or 'channel'
        context: {
            type: String,
        },
    },
    data: () => ({
        focused: false,
    }),
    computed: {
        hasDefaultValue() {
            return !this.value || this.value == this.defaultOrdering
        },
    },
    methods: {
        emitChange(ordering) {
            this.$emit("orderingChange", ordering)
        },
        setDefault() {
            this.emitChange(this.defaultOrdering)
        },
    },
    i18n: {
        messages: {
            fr: {
                activeSort: "Tri actif",
                setdefault: "Revenir au tri par défaut",
                warningListSorted: "Cette liste est triée selon un ordre particulier.",
                orderingIsShared:
                    "Cet ordre de tri de la page est sauvegardé pour tous les utilisateurs",
            },
            en: {
                activeSort: "Sorted",
                setdefault: "Return to default sorting",
                warninListSorted: "This list is sorted in a particular order.",
                orderingIsShared: "This ordering is saved for all users",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.OrderingSelector__list {
    @apply flex flex-col;
    width: 350px;
}
</style>
