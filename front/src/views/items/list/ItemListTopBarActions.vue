<template>
<Fragment>
    <span v-if="currentRouteName === 'itemList-active'">
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
                        loadingName="exportAllItems"
                        @confirmed="exportAllItems()"
                    />
                </div>
            </template>
        </Popper>
        <button
            class="button is-blue"
            @click="openOffPanel('addItem')"
        >
            {{ $t("newContent") }}
        </button>
    </span>

    <!-- The span is required to prevent Vue error with component reuse -->
    <span v-if="currentRouteName == 'itemList-filter'">
        <SavedFilterActions />
    </span>
</Fragment>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { $httpX } from "@js/ajax"
import urls from "@js/urls"
import PilotMixin from "@components/PilotMixin"
import { Fragment } from "vue-fragment"

import MenuItemWithConfirm from "@components/MenuItemWithConfirm"
import SavedFilterActions from "@views/savedFilters/SavedFilterActions.vue"

export default {
    name: "ItemListTopBarActions",
    mixins: [PilotMixin],
    components: {
        Fragment,
        MenuItemWithConfirm,
        SavedFilterActions,
    },
    data: () => ({
        exportStarted: false,
    }),
    methods: {
        exportAllItems() {
            $httpX({
                name: "exportAllItems",
                method: "PUT",
                url: urls.itemsExportAll,
                commit: this.$store.commit,
            }).then(() => (this.exportStarted = true))
        },
    },
    i18n: {
        messages: {
            fr: {
                exportAll: "Exporter tous les contenus (.xlsx)",
            },
            en: {
                exportAll: "Export all contents (.xlsx)",
            },
        },
    },
}
</script>
