<template>
<div class="AdminListActions">
    <template v-if="deletionRequested">
        <a
            class="button is-white"
            @click="
                deletionRequested = false
                $emit('deletionCancelled')
            "
        >
            {{ $t("cancel") }}
        </a>
        <a
            class="button is-red ml-2"
            @click="$emit('delete')"
        >
            {{ $t("confirmDeletion") }}
        </a>
    </template>
    <template v-else>
        <AdminButton
            aClass="button text-blue-600 mr-2 sm:ml-4"
            :checkPerm="checkPerm"
            @click="$emit('edit')"
        >
            {{ $t("edit") }}
        </AdminButton>
        <AdminButton
            aClass="button text-gray-600"
            :checkPerm="checkPerm"
            @click="
                deletionRequested = true
                $emit('deletionRequested')
            "
        >
            {{ $t("delete") }}
        </AdminButton>
    </template>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

import AdminButton from "@components/admin/AdminButton"

export default {
    name: "AdminListActions",
    components: {
        AdminButton,
    },
    props: {
        checkPerm: {
            type: Boolean,
            default: true,
        },
    },
    data: () => ({
        deletionRequested: false,
    }),
}
</script>

<style lang="scss">
.AdminListActions {
    @apply flex flex-shrink-0;
}
</style>
