<template>
<OffPanel name="savedFilterDelete">
    <div slot="offPanelTitle">{{ $t("delete") }}</div>
    <div slot="offPanelBody">
        <div
            v-if="selectedSavedFilter"
            class="alert-panel is-red"
        >
            <div>{{ $t("warningSavedFilterDeletion") }} : {{ selectedSavedFilter.title }}</div>
            <div>
                <SmartButtonSpinner
                    class="alert"
                    name="deleteSavedFilter"
                    :timeout="1000"
                    @click="confirmSavedFilterDeletion"
                >
                    {{ $t("confirmDeletion") }}
                </SmartButtonSpinner>
                <button
                    class="button default hollow"
                    @click="closeOffPanel('savedFilterDelete')"
                >
                    {{ $t("cancel") }}
                </button>
            </div>
        </div>
    </div>
</OffPanel>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "SavedFilterDeletePanel",
    mixins: [PilotMixin],
    props: {
        goToAfterDelete: {
            type: String,
            required: true,
        },
    },
    computed: {
        ...mapGetters("savedFilter", ["selectedSavedFilter"]),
    },
    methods: {
        ...mapMutations("savedFilter", ["removeSavedFilter"]),
        ...mapActions("savedFilter", ["deleteSavedFilter"]),
        confirmSavedFilterDeletion() {
            this.deleteSavedFilter(this.selectedSavedFilter).then(() => {
                this.removeSavedFilter(this.selectedSavedFilter)
                this.$router.push({ name: this.goToAfterDelete })
                this.closeOffPanel("savedFilterDelete")
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                warningSavedFilterDeletion:
                    "Attention : Vous allez supprimer définitivement le filtre",
            },
            en: {
                warningSavedFilterDeletion: "Warning: You will permanently delete the filter",
            },
        },
    },
}
</script>
