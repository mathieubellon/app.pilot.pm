<template>
<MainLayout class="DeskApp">
    <template #title>{{ $t("desk") }} {{ desk.name }}</template>

    <template #actions>
        <span v-if="$route.name === 'export'">
            <button
                v-if="!exportLaunched"
                class="button is-blue"
                @click="launchExport()"
            >
                {{ $t("launchExport") }}
            </button>
        </span>
    </template>

    <template #middlebar>
        <div class="tabs">
            <router-link
                class="tab"
                active-class="is-active"
                :to="{ name: 'edit' }"
            >
                {{ $t("edit") }}
            </router-link>
            <router-link
                class="tab"
                active-class="is-active"
                :to="{ name: 'config' }"
            >
                {{ $t("config") }}
            </router-link>
            <router-link
                class="tab"
                active-class="is-active"
                :to="{ name: 'export' }"
            >
                {{ $t("export") }}
            </router-link>
        </div>
    </template>

    <template #content>
        <div class="container mx-auto p-5">
            <div class="simple-panel">
                <router-view
                    :deskModel="deskModel"
                    :validation="$v"
                />
            </div>
        </div>
    </template>
</MainLayout>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { required } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"

export default {
    name: "DeskApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
    },
    data: () => ({
        deskModel: {
            id: null,

            name: "",
            logo: null,

            private_items_enabled: null,
            creation_forms_fields_visibles_by_default: null,
            item_languages_enabled: null,
            allowed_languages: [],
        },
    }),
    validations: {
        deskModel: {
            name: { required },
        },
    },
    computed: {
        ...mapState("desk", ["desk", "exportLaunched"]),
    },
    methods: {
        ...mapActions("desk", ["fetchDesk", "fetchExports", "fetchLanguages", "launchExport"]),
    },
    created() {
        this.fetchDesk().then((desk) => {
            this.deskModel = _.pick(this.desk, [
                "id",
                "name",
                "private_items_enabled",
                "creation_forms_fields_visibles_by_default",
                "item_languages_enabled",
                "allowed_languages",
            ])
        })
        this.fetchExports()
        this.fetchLanguages()
    },
    i18n: {
        messages: {
            fr: {
                config: "Configuration",
                edit: "Modifier",
                export: "Export",
                launchExport: "Lancer un export",
            },
            en: {
                config: "Configuration",
                edit: "Edit",
                export: "Export",
                launchExport: "Launch an export",
            },
        },
    },
}
</script>
