<template>
<App>
    <MainLayout slot="main">
        <slot
            name="title"
            slot="title"
        />
        <slot
            name="middlebar"
            slot="middlebar"
        />
        <slot
            name="content"
            slot="content"
        />
    </MainLayout>
</App>
</template>

<script>
import App from "./App.vue"
import MainLayout from "./MainLayout.vue"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "FullLayout",
    mixins: [PilotMixin],
    components: {
        App,
        MainLayout,
    },
}
</script>
