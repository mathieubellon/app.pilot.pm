<template>
<Modal
    class="ItemFreezeModal"
    name="freezeItem"
    :adaptive="true"
    height="95%"
    :max-height="500"
    :max-width="800"
    :pivotY="0.2"
    width="100%"
    @opened="onModalOpened"
>
    <div class="p-4">
        <div class="mb-4 p-2 text-lg bg-yellow-100">
            {{ $t("freezeConfirmMessage") }}
        </div>

        <div class="mb-4">
            <RichTextInput
                v-model="message"
                :excludeMenuBarItems="['heading', 'undo', 'redo', 'options']"
                :placeholder="$t('addMessage')"
            />
        </div>

        <div class="flex">
            <SmartButtonSpinner
                class="button is-yellow is-outlined mr-2"
                name="partialUpdateItem"
                :timeout="0"
                @click="validateMessageEdition"
            >
                {{ $t("okFreeze") }}
            </SmartButtonSpinner>

            <button
                class="button is-white"
                @click="endMessageEdition"
            >
                {{ $t("cancel") }}
            </button>
        </div>
    </div>
</Modal>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ItemFreezeModal",
    mixins: [PilotMixin],
    data: () => ({
        message: null,
    }),
    methods: {
        ...mapActions("itemDetail", ["toggleFrozen"]),
        onModalOpened() {
            this.message = null
        },
        validateMessageEdition() {
            this.toggleFrozen(this.message).then(this.endMessageEdition)
        },
        endMessageEdition() {
            this.$modal.hide("freezeItem")
        },
    },
    i18n: {
        messages: {
            fr: {
                addMessage: "Ajouter un message pour les autres utilisateurs",
                freezeConfirmMessage:
                    "Le contenu ne pourra plus être édité tant qu'il sera verrouillé.",
                okFreeze: "Ok, verrouiller",
            },
            en: {
                addMessage: "Ajouter un message pour les autres utilisateurs",
                freezeConfirmMessage: "The content won't be editable while it's locked",
                okFreeze: "Ok, freeze",
            },
        },
    },
}
</script>

<style lang="scss">
// This is needed to get the modal below the RichTextMenuBr poppers ( Popper=100 )
.ItemFreezeModal {
    z-index: 99;
}
</style>
