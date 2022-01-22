<template>
<div class="AssetDetailTabs tabs">
    <router-link
        class="tab"
        active-class="is-active"
        to="informations"
    >
        <Icon
            class="mr-1"
            name="Info"
        />
        {{ $t("infos") }}
    </router-link>
    <router-link
        class="tab"
        active-class="is-active"
        to="usageRights"
    >
        <Icon
            class="mr-1"
            name="File"
        />
        {{ $t("usageRights") }}
    </router-link>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "AssetDetailTabs",
    mixins: [PilotMixin],
    i18n: {
        messages: {
            fr: {
                usageRights: "Droits d'utilisation",
            },
            en: {
                usageRights: "Usage rights",
            },
        },
    },
}
</script>
