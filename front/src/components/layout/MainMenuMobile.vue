<template>
<OffPanel
    class="OffPanel MainMenuMobile"
    name="MainMenuPanel"
    position="left"
    width="100%"
>
    <template slot="offPanelBody">
        <MainMenu class="w-full rounded" />
    </template>
</OffPanel>
</template>

<script>
import PilotMixin from "@components/PilotMixin"
import MainMenu from "./MainMenu"

export default {
    name: "MainMenuMobile",
    mixins: [PilotMixin],
    components: {
        MainMenu,
    },
}
</script>

<style lang="scss">
.MainMenuMobile {
    background: #303e4d;

    .MainMenu {
        position: absolute;
        left: 0;
        margin-top: 3em;
        padding: 1em;
        width: 100%;
    }

    .MainMenu_element {
        padding: 0.3em 0;
    }
}
</style>
