<template>
<div class="tabs">
    <router-link
        class="tab"
        active-class="is-active"
        to="active"
    >
        {{ $t("actives") }}
    </router-link>
    <router-link
        class="tab"
        active-class="is-active"
        to="closed"
    >
        {{ $t("closed") }}
    </router-link>
</div>
</template>

<script>
export default {
    name: "ChannelTabs",
    i18n: {
        messages: {
            fr: {
                actives: "Actifs",
                closed: "Fermés",
            },
            en: {
                actives: "Actives",
                closed: "Closed",
            },
        },
    },
}
</script>
