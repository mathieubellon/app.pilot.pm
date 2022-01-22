<template>
<div class="tabs flex flex-grow">
    <router-link
        class="tab flex items-center"
        active-class="is-active"
        to="idea"
    >
        {{ $t("suggested") }}
    </router-link>
    <router-link
        class="tab"
        active-class="is-active"
        to="active"
    >
        {{ $t("actives") }}
    </router-link>
    <router-link
        class="tab mr-2"
        active-class="is-active"
        to="closed"
    >
        {{ $t("closed") }}
    </router-link>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ProjectTabs",
    mixins: [PilotMixin],
    i18n: {
        messages: {
            fr: {
                actives: "Actifs",
                closed: "Fermés",
                suggested: "Proposés",
            },
            en: {
                actives: "Actives",
                closed: "Closed",
                suggested: "Suggested",
            },
        },
    },
}
</script>
