<template>
<span class="Deletarium">
    <!-- It's VERY VERY important to use v-show instead of v-if here,
    so the Popper document click handler can find the target of the event -->
    <span v-show="!deletionRequested">
        <slot
            name="notRequested"
            :requestDeletion="requestDeletion"
        >
            <slot />
            <a
                :class="deleteButtonClass"
                @click="deletionRequested = true"
            >
                {{ deleteButtonText }}
            </a>
        </slot>
    </span>

    <div
        v-show="deletionRequested"
        class="alert-panel is-red"
    >
        <div class="text-semibold text-gray-800">{{ confirmDeletionMessage }}</div>

        <SmartButtonSpinner
            class="button is-red"
            :name="loadingName"
            :timeout="1000"
            @click="$emit('delete')"
        >
            {{ confirmDeleteButtonText }}
        </SmartButtonSpinner>
        <button
            class="button"
            @click="deletionRequested = false"
        >
            {{ $t("cancel") }}
        </button>
    </div>
</span>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

import SmartButtonSpinner from "@components/SmartButtonSpinner.vue"

export default {
    name: "Deletarium",
    components: {
        SmartButtonSpinner,
    },
    props: {
        loadingName: String,
        confirmDeleteButtonText: {
            type: String,
            default() {
                return this.$t("confirmDeletion")
            },
        },
        deleteButtonText: {
            type: String,
            default() {
                return this.$t("delete")
            },
        },
        deleteButtonClass: {
            type: String,
            default: "button text-red-800 bg-red-100",
        },
        confirmDeletionMessage: {
            type: String,
            default() {
                return this.$t("confirmDeletionMessage")
            },
        },
    },
    data: () => ({
        deletionRequested: false,
    }),
    watch: {
        deletionRequested(value) {
            this.$emit("deletionRequested", value)
        },
    },
    methods: {
        requestDeletion() {
            this.deletionRequested = true
        },
    },
}
</script>
