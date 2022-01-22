<template>
<MainLayout>
    <template #title>
        {{ $t("itemsTypes") }}
    </template>

    <template #actions>
        <AdminButton
            v-show="currentRouteName == 'itemTypesList'"
            @click="openOffPanel('itemTypeForm')"
        >
            {{ $t("addItemType") }}
        </AdminButton>
    </template>

    <template #content>
        <div class="container mx-auto p-5">
            <transition
                slot="main"
                enter-active-class="animated animated-150 fadeIn"
                leave-active-class="animated animated-150 fadeOut"
                mode="out-in"
            >
                <router-view />
            </transition>
        </div>
    </template>
</MainLayout>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"
import AdminButton from "@components/admin/AdminButton"

export default {
    name: "ItemTypeAdminApp",
    mixins: [PilotMixin],
    components: {
        AdminButton,
        MainLayout,
    },
    methods: {
        ...mapActions("itemTypes", ["fetchItemTypes", "fetchContentFieldSpecs"]),
    },
    created() {
        this.fetchContentFieldSpecs()
        this.fetchItemTypes()
    },
    i18n: {
        messages: {
            fr: {
                addItemType: "Ajouter un type de contenu",
            },
            en: {
                addItemType: "Add an item type",
            },
        },
    },
}
</script>
