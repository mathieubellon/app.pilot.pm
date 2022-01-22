<template>
<div>
    <div
        v-if="loadingName && loadingErrors[loadingName]"
        class="menu-item is-red"
    >
        <Icon
            v-if="iconName"
            :name="iconName"
        />
        <LoadingError
            label=""
            :name="loadingName"
        />
    </div>
    <button
        v-else-if="!confirmOpened"
        class="menu-item"
        :class="{
            disabled: disabled,
            'is-red': isRed && !disabled,
            'is-yellow': isYellow && !disabled,
        }"
        v-tooltip="tooltip || null"
        @click="onMenuItemClick"
    >
        <Icon
            v-if="iconName"
            :name="iconName"
        />
        <BarLoader v-if="isLoading" />
        <template v-else>{{ label }}</template>
    </button>
    <div
        v-else
        class="flex flex-col w-full p-4 my-2 bg-gray-100 rounded"
    >
        <div class="text-gray-800 text-sm font-bold mb-1">
            {{ confirmTitle ? confirmTitle : label + " ?" }}
        </div>
        <div
            v-if="confirmMessage"
            class="text-gray-600 text-sm font-medium mb-4"
        >
            {{ confirmMessage }}
        </div>
        <button
            class="button is-small w-full max-w-xs mb-2 confirmAction"
            :class="{
                'is-red': isRed,
                'is-yellow': isYellow,
                'is-blue': !isRed && !isYellow,
            }"
            @click="
                confirmOpened = false
                $emit('confirmed')
            "
        >
            {{ confirmButtonText ? confirmButtonText : $t("iAmSure") }}
        </button>
        <button
            class="button w-full is-small w-full max-w-xs"
            @click="confirmOpened = false"
        >
            {{ $t("cancel") }}
        </button>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { Fragment } from "vue-fragment"
import PilotMixin from "@components/PilotMixin"

import LoadingError from "@components/LoadingError"

export default {
    name: "MenuItemWithConfirm",
    mixins: [PilotMixin],
    components: {
        Fragment,
        LoadingError,
    },
    props: {
        label: String,
        confirmTitle: String,
        confirmMessage: String,
        confirmButtonText: String,
        iconName: String,
        isRed: Boolean,
        isYellow: Boolean,
        disabled: Boolean,
        tooltip: String,
        loading: Boolean,
        loadingName: String,
    },
    data: () => ({
        confirmOpened: false,
    }),
    computed: {
        ...mapState("loading", ["loadingInProgress", "loadingErrors"]),
        isLoading() {
            return this.loading || (this.loadingName && this.loadingInProgress[this.loadingName])
        },
    },
    methods: {
        onMenuItemClick() {
            if (this.disabled) {
                return
            }
            this.confirmOpened = true
        },
    },
}
</script>
