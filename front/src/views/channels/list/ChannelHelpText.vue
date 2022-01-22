<template>
<div class="help-text">
    <div class="help-text-title">
        <Icon
            class="help-text-icon"
            name="Channel"
        />
        <span>{{ $t("emptyState") }}</span>
    </div>
    <div class="help-text-content">
        {{ $t("helpTextContent") }}
    </div>
    <button
        class="button is-blue"
        slot="empty-state-content"
        @click.prevent="openOffPanel('addChannelForm')"
    >
        {{ $t("addButton") }}
    </button>
</div>
</template>

<script>
import { mapState, mapMutations, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ChannelHelpText",
    mixins: [PilotMixin],
    i18n: {
        messages: {
            fr: {
                emptyState: "Aucun canal",
                addButton: "Ajouter un canal",
                helpTextContent:
                    "Utilisez les canaux pour classer vos contenus par supports de diffusion (site, magazine, évènement, réseaux sociaux). ",
            },
            en: {
                emptyState: "No channel",
                addButton: "Add channel",
                helpTextContent:
                    "Use channels to organize your contents by distribution media (websites, magazines, events, social medias, even TVs in your corp. buildings). ",
            },
        },
    },
}
</script>
