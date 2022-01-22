<template>
<Fragment>
    <RichTextMenuBarItem
        name="createTable"
        :bubbleClick="true"
        :disabled="editor.isActive.table()"
        :inDropdown="true"
        :label="$t('createTable')"
        @click="onCreateTableClick"
    />

    <RichTextMenuBarItem
        name="addRowAfter"
        :disabled="!editor.isActive.table()"
        :inDropdown="true"
        :label="$t('addRowAfter')"
    />

    <RichTextMenuBarItem
        name="addRowBefore"
        :disabled="!editor.isActive.table()"
        :inDropdown="true"
        :label="$t('addRowBefore')"
    />

    <RichTextMenuBarItem
        name="deleteRow"
        :disabled="!editor.isActive.table()"
        :inDropdown="true"
        :label="$t('deleteRow')"
    />

    <RichTextMenuBarItem
        name="addColumnAfter"
        :disabled="!editor.isActive.table()"
        :inDropdown="true"
        :label="$t('addColumnAfter')"
    />

    <RichTextMenuBarItem
        name="addColumnBefore"
        :disabled="!editor.isActive.table()"
        :inDropdown="true"
        :label="$t('addColumnBefore')"
    />

    <RichTextMenuBarItem
        name="deleteColumn"
        :disabled="!editor.isActive.table()"
        :inDropdown="true"
        :label="$t('deleteColumn')"
    />

    <RichTextMenuBarItem
        name="toggleCellMerge"
        :disabled="!editor.isActive.table()"
        :inDropdown="true"
        :label="$t('toggleCellMerge')"
    />

    <RichTextMenuBarItem
        name="deleteTable"
        :disabled="!editor.isActive.table()"
        :inDropdown="true"
        :label="$t('deleteTable')"
    />
</Fragment>
</template>

<script>
import { Fragment } from "vue-fragment"
import RichTextMenuBarItem from "./RichTextMenuBarItem"

export default {
    name: "RichTextMenuBarTableItems",
    components: {
        Fragment,
        RichTextMenuBarItem,
    },
    inject: ["editor"],
    methods: {
        onCreateTableClick() {
            if (!this.editor.isActive.table()) {
                this.editor.commands.createTable({
                    rowsCount: 3,
                    colsCount: 3,
                    withHeaderRow: false,
                })
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                addColumnAfter: "Ajout colonne après",
                addColumnBefore: "Ajout colonne avant",
                addRowAfter: "Ajout ligne après",
                addRowBefore: "Ajout ligne avant",
                createTable: "Créer table",
                deleteColumn: "Supprimer colonne",
                deleteRow: "Supprimer ligne",
                deleteTable: "Supprimer table",
                toggleCellMerge: "Fusionner cellules",
            },
            en: {
                addColumnAfter: "Add column after",
                addColumnBefore: "Add column before",
                addRowAfter: "Add row after",
                addRowBefore: "Add row before",
                createTable: "Create table",
                deleteColumn: "Delete column",
                deleteRow: "Delete row",
                deleteTable: "Delete table",
                toggleCellMerge: "Cell merge",
            },
        },
    },
}
</script>
