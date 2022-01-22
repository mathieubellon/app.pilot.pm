<template>
<MainLayout>
    <template #title>
        {{ $t("targets") }}
    </template>

    <template #actions>
        <AdminButton @click="$refs.form.openFormPanel()">
            {{ $t("addTarget") }}
        </AdminButton>
    </template>

    <template #content>
        <div class="container mx-auto p-5">
            <Loadarium name="fetchTargets">
                <AdminList
                    :instancesList="sortedTargets"
                    :sortable="false"
                    @delete="validateTargetDeletion"
                    @edit="$refs.form.openFormPanel($event)"
                >
                    <div
                        class=""
                        slot-scope="{ instance }"
                    >
                        <div class="font-bold mb-1">
                            {{ instance.name }}
                        </div>

                        <div
                            v-html="getDescriptionHtml(instance)"
                            class="text-gray-600"
                        />
                    </div>
                </AdminList>

                <div
                    v-if="sortedTargets.length == 0"
                    class="help-text"
                >
                    <div class="help-text-title">
                        <Icon
                            class="help-text-icon"
                            name="Target"
                        />
                        <span>{{ $t("noTarget") }}</span>
                    </div>

                    <div class="help-text-content">
                        {{ $t("explainTargets") }}
                    </div>
                    <a
                        class="button is-blue"
                        @click.prevent="openOffPanel('targetForm')"
                    >
                        {{ $t("addTarget") }}
                    </a>
                </div>
            </Loadarium>

            <AutoFormInPanel
                name="targetForm"
                ref="form"
                :saveUrl="urls.targets"
                :schema="targetFormSchema"
                :title="$t('addTarget')"
                @created="onTargetCreated"
                @updated="onTargetUpdated"
            />
        </div>
    </template>
</MainLayout>
</template>

<script>
import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { EVENTS, dispatchEvent } from "@js/events"
import { sortByAlphaString } from "@js/utils.js"
import { richTextSchema } from "@richText/schema"
import PilotMixin from "@components/PilotMixin"
import MainLayout from "@components/layout/MainLayout"

import AdminButton from "@components/admin/AdminButton"
import AdminList from "@components/admin/AdminList.vue"

export default {
    name: "TargetAdminApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
        AdminButton,
        AdminList,
    },
    data: () => ({
        targets: null,
    }),
    computed: {
        sortedTargets() {
            return sortByAlphaString(this.targets, (target) => target.name)
        },
        targetFormSchema() {
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
                    type: "richText",
                    label: this.$t("description"),
                    placeholder: this.$t("description"),
                },
            ]
        },
    },
    methods: {
        onTargetCreated(target) {
            this.targets.push(target)
            dispatchEvent(EVENTS.targetCreated, target)
        },
        onTargetUpdated(target) {
            _.assign(_.find(this.targets, { id: target.id }), target)
            dispatchEvent(EVENTS.targetUpdated, target)
        },
        validateTargetDeletion(target) {
            $httpX({
                name: "deleteTarget",
                commit: this.$store.commit,
                method: "DELETE",
                url: urls.targets.format({ id: target.id }),
            }).then((response) => {
                this.targets = this.targets.filter((t) => t.id != target.id)
                dispatchEvent(EVENTS.targetDeleted, target)
            })
        },
        getDescriptionHtml(target) {
            return richTextSchema.HTMLFromJSON(target.description)
        },
    },
    created() {
        $httpX({
            name: "fetchTargets",
            method: "GET",
            commit: this.$store.commit,
            url: urls.targets,
        }).then((response) => {
            this.targets = response.data
        })
    },
    i18n: {
        messages: {
            fr: {
                addTarget: "Ajouter une cible",
                explainTargets:
                    "Les cibles vous permettent de définir des groupes de publics pour vos contenus et projets",
                noTarget: "Aucune cible",
            },
            en: {
                addTarget: "Add a target",
                explainTargets:
                    "Targets allow you to define audience groups for your content and projects",
                noTarget: "No target",
            },
        },
    },
}
</script>
