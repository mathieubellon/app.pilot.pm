<template>
<div class="ChannelFormAdd">
    <AutoForm
        :errorText="$t('channelCreationError')"
        :saveUrl="urls.channels"
        :schema="channelFormSchema"
        :successText="$t('channelCreated')"
        @cancel="closeForm"
        @saved="onChannelSaved"
    />
</div>
</template>

<script>
import { mapGetters, mapMutations, mapActions } from "vuex"
import { EVENTS, dispatchEvent } from "@js/events"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ChannelFormAdd",
    mixins: [PilotMixin],
    computed: {
        ...mapGetters("choices", ["channelChoices", "usersChoices"]),
        channelFormSchema() {
            return [
                {
                    name: "name",
                    type: "char",
                    label: this.$t("channelName"),
                    placeholder: this.$t("channelName"),
                    required: true,
                },
                {
                    name: "type_id",
                    type: "choice",
                    label: this.$t("type"),
                    choices: this.channelTypeChoices,
                },
                {
                    name: "owners_id",
                    type: "choice",
                    label: this.$t("owners"),
                    choices: this.usersChoices,
                    multiple: true,
                },
                {
                    name: "description",
                    type: "richText",
                    label: this.$t("description"),
                },
            ]
        },
        channelTypeChoices() {
            let labels = this.$store.state.labels.labels.channel_type || []
            return labels.map((channelType) => ({ value: channelType.id, label: channelType.name }))
        },
    },
    methods: {
        ...mapMutations("offPanel", ["closeOffPanel"]),
        ...mapActions("channelList", ["fetchChannelList"]),
        ...mapActions("labels", ["fetchLabels"]),
        onChannelSaved(channel) {
            dispatchEvent(EVENTS.channelCreated, channel)

            setTimeout(() => {
                this.closeForm()
            }, 1000)
        },
        closeForm() {
            this.closeOffPanel("addChannelForm")
        },
    },
    created() {
        this.fetchLabels("channel_type")
    },
    i18n: {
        messages: {
            fr: {
                channelCreated: "Canal créé avec succès",
                channelCreationError: "Erreur, le canal n'a pas été créé",
                channelName: "Nom du canal",
                parent: "Canal parent",
            },
            en: {
                channelCreated: "Channel successfully created",
                channelCreationError: "Error, the channel was not created",
                channelName: "Channel Name",
                parent: "Parent channel",
            },
        },
    },
}
</script>
