<template>
<OffPanel
    class="SavedFilterInternalSharePanel"
    name="SavedFilterInternalSharePanel"
    @opened="onOpen"
>
    <div slot="offPanelTitle">{{ $t("savedFilterShareTitle") }}</div>
    <div slot="offPanelBody">
        <BaseForm
            :errorText="$t('internalSharedFilterCreationError')"
            :model="model"
            :saveUrl="urls.internalSharedFilters"
            :successText="$t('internalSharedFilterCreated')"
            :vuelidate="$v.model"
            @cancel="closeOffPanel('SavedFilterInternalSharePanel')"
            @saved="onInternalSharedFilterSaved"
        >
            <div class="mb-4">
                <span v-html="$t('shareInstructions')" />
                <CommentBox
                    v-model="model.message"
                    ref="messageInput"
                    @input="$v.model.message.$touch()"
                />
                <ValidationErrors :validation="$v.model.message" />
            </div>
        </BaseForm>

        <div class="mt-8">
            <div class="font-bold text-lg mb-3">{{ $t("existingSharing") }}</div>

            <Loadarium name="fetchInternalSharedFilters">
                <div
                    v-if="internalSharedFilters.length == 0"
                    class="alert-panel is-blue"
                >
                    {{ $t("filterNotSharedYet") }}
                </div>
                <template v-else>
                    <div
                        v-for="sharedFilter in internalSharedFilters"
                        class="simple-panel mx-0"
                    >
                        <CommentDisplay :comment="sharedFilter.message" />

                        <div class="font-semibold">{{ $t("notifiedUsers") }}</div>
                        <div v-for="user in sharedFilter.users">
                            <UserDisplay
                                :user="user"
                                :withAvatar="true"
                            />
                        </div>
                    </div>
                </template>
            </Loadarium>
        </div>
    </div>
</OffPanel>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { required } from "vuelidate/lib/validators"
import { TextSelection } from "prosemirror-state"
import PilotMixin from "@components/PilotMixin"

import CommentBox from "@components/CommentBox.vue"
import CommentDisplay from "@components/CommentDisplay"

export default {
    name: "SavedFilterInternalSharePanel",
    mixins: [PilotMixin],
    components: {
        CommentDisplay,
        CommentBox,
    },
    data: () => ({
        model: {
            saved_filter_id: null,
            message: "@",
        },
    }),
    validations: {
        model: {
            message: { required },
        },
    },
    computed: {
        ...mapState("savedFilter", ["internalSharedFilters"]),
        ...mapGetters("savedFilter", ["selectedSavedFilter"]),
    },
    methods: {
        ...mapMutations("savedFilter", ["prependToInternalSharedFilters"]),
        ...mapMutations("offPanel", ["closeOffPanel"]),
        ...mapActions("savedFilter", ["fetchInternalSharedFilters"]),
        onInternalSharedFilterSaved(internalSharedFilter) {
            this.prependToInternalSharedFilters(internalSharedFilter)
        },
        onOpen() {
            this.model.saved_filter_id = this.selectedSavedFilter.id
            this.fetchInternalSharedFilters()

            setTimeout(() => {
                if (this.$refs.messageInput && this.$refs.messageInput.editor) {
                    let editor = this.$refs.messageInput.editor
                    // Position the cursor after the @
                    editor.dispatchTransaction(
                        editor.state.tr.setSelection(TextSelection.create(editor.state.doc, 2)),
                    )
                    // Then gain focus on the editor
                    editor.focus()
                }
            }, 500)
        },
    },
    i18n: {
        messages: {
            fr: {
                internalSharedFilterCreated: "Partage effectué avec succès",
                internalSharedFilterCreationError:
                    "Une erreur est survenue, le partage n'a pas été effectué",
                existingSharing: "Partage effectués",
                filterNotSharedYet: "Ce filtre n'a pas encore été partagée.",
                notifiedUsers: "Utilisateurs notifiés",
                savedFilterShareTitle: "Partager avec des utilisateurs du desk",
                shareInstructions:
                    "Utilisez la zone de texte ci-dessous pour choisir les destinataires du partage.<br />" +
                    "Tous les @mentionnés seront notifiés, et pourront voir et copier ce filtre.<br />" +
                    "Vous pouvez aussi y ajouter un message personnalisé.",
            },
            en: {
                internalSharedFilterCreated: "Sharing successfully completed",
                internalSharedFilterCreationError:
                    "An error has occurred, sharing has not been performed",
                existingSharing: "Sharing already done",
                filterNotSharedYet: "This filter has not yet been shared.",
                notifiedUsers: "Notified users",
                savedFilterShareTitle: "Share with other desk users",
                shareInstructions:
                    "Use the textarea below to chose who you want to share with.<br />" +
                    "Every @mentionee will be notified, and will be able to see and copy this filter.<br />" +
                    "You can also add a custom message for the recipients.",
            },
        },
    },
}
</script>
