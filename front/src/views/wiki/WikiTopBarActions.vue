<template>
<Fragment>
    <template v-if="wikiPageInEdition">
        <button
            class="button ml-2"
            key="cancelEdition"
            @click="cancelEdition"
        >
            {{ $t("cancel") }}
        </button>

        <SmartButtonSpinner
            class="button is-blue ml-2"
            name="saveWikiPage"
            key="saveEdition"
            @click="saveEdition"
        >
            {{ $t("save") }}
        </SmartButtonSpinner>
    </template>

    <template v-else>
        <AdminButton
            key="startWikiPageEdition"
            aClass="button ml-8 "
            @click="startWikiPageEdition"
        >
            {{ $t("edit") }}
        </AdminButton>
        <AdminButton
            key="startWikiPageCreation"
            aClass="button is-blue ml-2 "
            @click="startWikiPageCreation"
        >
            {{ $t("newPage") }}
        </AdminButton>
        <AdminButton
            v-if="!wikiPage.is_home_page"
            key="deleteWikiPage"
            aClass="button is-red ml-2 "
            @click="$modal.show('deleteWikiPage')"
        >
            {{ $t("delete") }}
        </AdminButton>
    </template>

    <!-- Need the span for <Modal> to work inside a <Fragment> -->
    <span>
        <Modal
            name="deleteWikiPage"
            height="auto"
            :pivotY="0.15"
        >
            <div class="p-8">
                <div class="text-red-500 font-bold mb-4">
                    {{ $t("wikiPageDeletionWarning", { wikiPageName: wikiPage.name }) }}
                    <br />
                </div>

                <button
                    class="button mr-2"
                    @click="$modal.hide('deleteWikiPage')"
                >
                    {{ $t("cancel") }}
                </button>
                <SmartButtonSpinner
                    class="button is-red"
                    name="deleteWikiPage"
                    @click="confirmDeletion"
                >
                    {{ $t("confirmDeletion") }}
                </SmartButtonSpinner>
            </div>
        </Modal>
    </span>
</Fragment>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import urls from "@js/urls"
import PilotMixin from "@components/PilotMixin"
import { Fragment } from "vue-fragment"

import AdminButton from "@components/admin/AdminButton"

export default {
    name: "WikiTopBarActions",
    mixins: [PilotMixin],
    components: {
        Fragment,
        AdminButton,
    },
    computed: {
        ...mapState("wiki", ["wikiPage", "wikiPageInEdition", "wikiPageInEditionValidation"]),
    },
    methods: {
        ...mapMutations("wiki", ["setWikiPageInEdition"]),
        ...mapActions("wiki", [
            "createWikiPage",
            "updateWikiPage",
            "deleteWikiPage",
            "startWikiPageCreation",
            "startWikiPageEdition",
        ]),
        cancelEdition() {
            this.setWikiPageInEdition(null)
        },
        saveEdition() {
            this.wikiPageInEditionValidation.$touch()

            if (this.wikiPageInEditionValidation.$invalid) {
                return
            }

            let isCreation = !Boolean(this.wikiPageInEdition.id)
            let saveWikiPage = isCreation ? this.createWikiPage : this.updateWikiPage
            saveWikiPage(this.wikiPageInEdition).then(() => {
                this.setWikiPageInEdition(null)
                if (isCreation) {
                    this.$router.push(this.wikiPage.url)
                }
            })
        },
        confirmDeletion() {
            this.deleteWikiPage(this.wikiPage).then(() => {
                this.$modal.hide("deleteWikiPage")
                this.$router.push(urls.wikiApp.url)
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                newPage: "Nouvelle page",
                wikiPageDeletionWarning:
                    'Êtes-vous sûr de vouloir supprimer la page de wiki "{wikiPageName}" ?',
            },
            en: {
                newPage: "New page",
                wikiPageDeletionWarning:
                    'Are you sure you want to delete the wiki page& "{wikiPageName}" ?',
            },
        },
    },
}
</script>
