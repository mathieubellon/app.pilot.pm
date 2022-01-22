<template>
<MainLayout>
    <template #title>
        {{ $t("integrations") }}
    </template>

    <template #actions>
        <AdminButton @click="$refs.form.openFormPanel()">
            {{ $t("addToken") }}
        </AdminButton>
    </template>

    <template #content>
        <div class="container mx-auto p-5">
            <Loadarium name="fetchTokens">
                <AdminList
                    :instancesList="sortedTokens"
                    :sortable="false"
                    @delete="validateTokenDeletion"
                    @edit="$refs.form.openFormPanel($event)"
                >
                    <div
                        class="flex flex-col flex-grow"
                        slot-scope="{ instance }"
                    >
                        <span class="TokenAdminApp__name font-bold mb-1">
                            {{ instance.name }}
                        </span>

                        <span class="TokenAdminApp__token w-full">
                            <input
                                readonly
                                type="text"
                                :value="instance.token"
                            />
                        </span>

                        <span
                            class="TokenAdminApp__description text-gray-600 font-medium text-sm mt-2"
                        >
                            {{ instance.description }}
                        </span>
                    </div>
                </AdminList>

                <div
                    v-if="sortedTokens.length == 0"
                    class="help-text"
                >
                    <div class="help-text-title">{{ $t("noToken") }}</div>
                    <div class="help-text-content">
                        {{ $t("explainTokens") }}
                    </div>
                </div>
            </Loadarium>

            <AutoFormInPanel
                name="tokenForm"
                ref="form"
                :saveUrl="urls.integrationsApiTokens"
                :schema="tokenFormSchema"
                :title="$t('addToken')"
                @created="onTokenCreated"
                @updated="onTokenUpdated"
            />
        </div>
    </template>
</MainLayout>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"
import MainLayout from "@components/layout/MainLayout"

import AdminButton from "@components/admin/AdminButton"
import AdminList from "@components/admin/AdminList.vue"

export default {
    name: "TokenAdminApp",
    mixins: [PilotMixin],
    components: {
        AdminButton,
        AdminList,
        MainLayout,
    },
    data: () => ({
        tokens: null,
    }),
    computed: {
        sortedTokens() {
            return sortByAlphaString(this.tokens, (token) => token.name)
        },
        tokenFormSchema() {
            return [
                {
                    name: "name",
                    type: "char",
                    label: this.$t("name"),
                    placeholder: this.$t("name"),
                    required: true,
                },
                {
                    name: "description",
                    type: "text",
                    label: this.$t("description"),
                    placeholder: this.$t("description"),
                },
            ]
        },
    },
    methods: {
        onTokenCreated(token) {
            this.tokens.push(token)
        },
        onTokenUpdated(token) {
            _.assign(_.find(this.tokens, { id: token.id }), token)
        },
        validateTokenDeletion(token) {
            $httpX({
                name: "deleteToken",
                commit: this.$store.commit,
                method: "DELETE",
                url: urls.integrationsApiTokens.format({ id: token.id }),
            }).then((response) => {
                this.tokens = this.tokens.filter((t) => t.id != token.id)
            })
        },
    },
    created() {
        $httpX({
            name: "fetchTokens",
            method: "GET",
            commit: this.$store.commit,
            url: urls.integrationsApiTokens,
        }).then((response) => {
            this.tokens = response.data
        })

        // Each external form display its public link into a read-only input.
        // When the user click on that input, select all its content for an easy copy-paste
        $(document).on("click.TokenAdminApp", ".TokenAdminApp__token input", function () {
            $(this).select()
        })
    },
    i18n: {
        messages: {
            fr: {
                addToken: "Ajouter un token",
                explainTokens:
                    "Les jetons permettent de se connecter à l'API d'integration de Pilot",
                integrations: "Integrations",
                noToken: "Aucun jeton",
            },
            en: {
                addToken: "New token",
                explainTokens: "Tokens allows to connect to the Pilot integration API",
                integrations: "Integrations",
                noToken: "No token",
            },
        },
    },
}
</script>
