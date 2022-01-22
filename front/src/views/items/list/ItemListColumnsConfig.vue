<template>
<Popper
    v-if="myPermissions.is_admin"
    class="ItemListColumnsConfig"
    triggerElementName="ItemListColumnsConfigPopperRef"
    triggerType="click"
>
    <template #triggerElement>
        <button
            class="list-action-button"
            ref="ItemListColumnsConfigPopperRef"
            type="button"
        >
            {{ $t("options") }}
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
        <div class="ItemListColumnsConfig__popper">
            <div class="bg-blue-300 text-blue-900 text-sm font-medium p-2 rounded-t">
                {{ $t("adminOnly") }}
            </div>
            <div class="bg-blue-100 text-blue-800 text-sm p-2 rounded rounded-t-none">
                {{ $t("columnConfigIsShared") }}
            </div>

            <div class="text-sm font-bold mt-2 pl-1">
                {{ $t("columnConfig") }}
            </div>

            <label
                v-for="columnSpec in columnsSpecs"
                class="menu-item block font-medium text-sm py-1"
                :key="columnSpec.name"
            >
                <ToggleButton
                    class="toggle mr-2"
                    :disabled="columnSpec.required"
                    :sync="true"
                    :value="itemListColumns[columnSpec.name]"
                    @input="toggleColumn(columnSpec.name)"
                />
                {{ columnSpec.label }}
            </label>
        </div>
    </template>
</Popper>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import { getMainItemListName } from "@/store/modules/ListConfigStore"

import { ToggleButton } from "vue-js-toggle-button"

export default {
    name: "ItemListColumnsConfig",
    mixins: [PilotMixin],
    components: {
        ToggleButton,
    },
    props: {
        // Can be null or 'project' or 'channel'
        context: {
            type: String,
        },
    },
    computed: {
        ...mapState("listConfig", ["ITEM_LIST_COLUMNS_SPEC", "listConfigs"]),
        ...mapGetters("listConfig", ["itemListColumns"]),
        ...mapGetters("users", ["myPermissions"]),
        columnsSpecs() {
            let specs = this.ITEM_LIST_COLUMNS_SPEC
            if (this.context == "project") {
                _.remove(specs, (s) => s.name == "project")
            }
            if (this.context == "channel") {
                _.remove(specs, (s) => s.name == "channels")
            }
            return specs
        },
    },
    methods: {
        ...mapMutations("listConfig", ["setColumnsConfig"]),
        ...mapActions("listConfig", ["partialUpdateListConfig"]),
        toggleColumn(name) {
            let listName = getMainItemListName()
            let updatedColumns = _.cloneDeep(this.itemListColumns)
            updatedColumns[name] = !updatedColumns[name]
            this.setColumnsConfig(updatedColumns) // Assume the server-side update will be ok
            this.partialUpdateListConfig({
                name: listName,
                listConfig: {
                    columns: updatedColumns,
                },
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                adminOnly: "Visible uniquement par un admin",
                columnConfig: "Afficher les colonnes",
                columnConfigIsShared:
                    "Cette configuration est sauvegardée pour tous les utilisateurs ",
            },
            en: {
                adminOnly: "Only visible by admin",
                columnConfig: "Display columns",
                columnConfigIsShared: "This configuration is saved for all users",
            },
        },
    },
}
</script>

<style lang="scss">
.ItemListColumnsConfig__popper {
    width: 300px;
}
</style>
