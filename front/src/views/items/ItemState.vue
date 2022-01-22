<template>
<div class="flex items-center w-full">
    <svg
        v-if="showBullet"
        class="feather feather-circle h-3 w-3 mx-1 fill-current flex-shrink-0"
        :class="{ muted: muted }"
        :style="{ color: state && !muted && state.color }"
        fill="none"
        stroke="transparent"
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
    >
        <circle
            cx="12"
            cy="12"
            r="10"
        ></circle>
    </svg>
    <div
        v-if="showStateText"
        class="truncate"
    >
        <template v-if="state">{{ state.label }}</template>
        <template v-else>{{ $t("noState") }}</template>
    </div>
</div>
</template>

<script>
export default {
    name: "ItemState",
    props: {
        state: Object,
        muted: Boolean,
        showStateText: {
            type: Boolean,
            default: true,
        },
        showBullet: {
            type: Boolean,
            default: true,
        },
    },
    i18n: {
        messages: {
            fr: {
                noState: "Aucun statut",
            },
            en: {
                noState: "No status",
            },
        },
    },
}
</script>
