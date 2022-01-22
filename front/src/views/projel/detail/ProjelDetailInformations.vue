<template>
<div class="ProjelDetailInformations">
    <div
        v-if="viewportPhone"
        class="flex flex-col"
    >
        <ProjelDetailDescription />
        <ProjelDetailSideBar />
        <ItemListForProjel />
    </div>
    <div
        v-else
        class="flex"
    >
        <div class="w-1/3 mr-6">
            <ProjelDetailSideBar />
        </div>

        <div class="flex flex-col w-2/3 max-w-screen-md">
            <ProjelDetailDescription />
            <ItemListForProjel />
        </div>
    </div>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"
import ResponsiveMixin from "@components/ResponsiveMixin"

import ProjelDetailSideBar from "./ProjelDetailSidebar"
import ProjelDetailDescription from "./ProjelDetailDescription"
import ItemListForProjel from "./ItemListForProjel"

export default {
    name: "ProjelDetailInformations",
    mixins: [PilotMixin, ResponsiveMixin],
    components: {
        ProjelDetailSideBar,
        ProjelDetailDescription,
        ItemListForProjel,
    },
}
</script>
