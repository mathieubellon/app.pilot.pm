<template>
<div class="flex overflow-hidden">
    <transition
        enter-active-class="animated fadeInLeft"
        leave-active-class="animated fadeOutLeft"
    >
        <div
            v-if="isSidebarHierarchyVisible && viewportGTETablet"
            class="mr-6 w-1/4"
        >
            <ProjelDetailSidebarHierarchy />
        </div>
    </transition>

    <div
        class="ProjelDetailContents__contents w-full"
        :class="{ 'md:w-3/4': isSidebarHierarchyVisible }"
    >
        <ItemListForProjel />
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import ResponsiveMixin from "@components/ResponsiveMixin"

import ItemListForProjel from "./ItemListForProjel"
import ProjelDetailSidebarHierarchy from "./ProjelDetailSidebarHierarchy.vue"

export default {
    name: "ProjelDetailContents",
    mixins: [PilotMixin, ResponsiveMixin],
    components: {
        ItemListForProjel,
        ProjelDetailSidebarHierarchy,
    },
    computed: {
        ...mapGetters("projelDetail", ["isSidebarHierarchyVisible"]),
    },
}
</script>
