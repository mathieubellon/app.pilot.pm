<template>
<AutoForm
    :errorText="$t('deskCreationError')"
    :saveUrl="urls.desks"
    :schema="deskFormSchema"
    :successText="$t('deskCreated')"
    @cancel="closeOffPanel('newDesk')"
    @saved="onDeskSaved"
/>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "DeskFormAdd",
    mixins: [PilotMixin],
    computed: {
        deskFormSchema() {
            return [
                {
                    name: "name",
                    type: "char",
                    label: this.$t("name"),
                    placeholder: this.$t("name"),
                    required: true,
                },
            ]
        },
    },
    methods: {
        ...mapMutations("offPanel", ["closeOffPanel"]),
        onDeskSaved() {
            // When the desk is created, we're connected to it by the API.
            // Redirect to the dashboard of this new desk
            setTimeout(() => {
                window.location = "/"
            }, 500)
        },
    },
    i18n: {
        messages: {
            fr: {
                deskCreated: "Desk créé, redirection en cours...",
                deskCreationError: "Une erreur est survenue, le desk n'a pas été créé",
            },
            en: {
                deskCreated: "Desk created, redirection in progress...",
                deskCreationError: "Error : Desk not created",
            },
        },
    },
}
</script>
