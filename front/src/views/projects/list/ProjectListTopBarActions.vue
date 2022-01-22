<template>
<Fragment>
    <span v-if="$route.name === 'projectList-active'">
        <Popper
            triggerElementName="PopperRef"
            triggerType="click"
        >
            <template #triggerElement>
                <button
                    class="button is-topbar"
                    ref="PopperRef"
                >
                    {{ $t("actions") }}
                    <!-- The empty span is required to correctly align with flex display -->
                    <span>
                        <Icon
                            class="caret"
                            name="ChevronDown"
                        />
                    </span>
                </button>
            </template>

            <template #content>
                <div class="w-64">
                    <div
                        v-if="exportStarted"
                        class="p-4 font-semibold text-green-500"
                    >
                        ✓ {{ $t("exportStarted") }}
                    </div>
                    <MenuItemWithConfirm
                        v-else
                        :confirmButtonText="$t('confirmExportAll')"
                        :confirmMessage="$t('youWillBeNotifiedAfterExport')"
                        iconName="Export"
                        :label="$t('exportAll')"
                        loadingName="exportAllProjects"
                        @confirmed="exportAllProjects()"
                    />
                </div>
            </template>
        </Popper>
        <button
            class="button is-blue"
            @click.prevent="openOffPanel('addActiveProjectForm')"
        >
            {{ $t("newProject") }}
        </button>
    </span>

    <button
        v-if="$route.name === 'projectList-idea'"
        class="button is-blue"
        @click.prevent="openOffPanel('addIdeaProjectForm')"
    >
        {{ $t("newDraft") }}
    </button>
</Fragment>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { $httpX } from "@js/ajax"
import urls from "@js/urls"
import PilotMixin from "@components/PilotMixin"
import { Fragment } from "vue-fragment"

import MenuItemWithConfirm from "@components/MenuItemWithConfirm"

export default {
    name: "ProjectListTopBarActions",
    mixins: [PilotMixin],
    components: {
        Fragment,
        MenuItemWithConfirm,
    },
    data: () => ({
        exportStarted: false,
    }),
    methods: {
        exportAllProjects() {
            $httpX({
                name: "exportAllProjects",
                method: "PUT",
                url: urls.projectsExportAll,
                commit: this.$store.commit,
            }).then(() => (this.exportStarted = true))
        },
    },
    i18n: {
        messages: {
            fr: {
                newDraft: "Nouvelle proposition",
                exportAll: "Exporter tous les projets (.xlsx)",
            },
            en: {
                newDraft: "New suggestion",
                exportAll: "Export all projects (.xlsx)",
            },
        },
    },
}
</script>
