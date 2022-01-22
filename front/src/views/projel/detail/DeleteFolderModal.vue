<template>
<Modal
    name="deleteFolder"
    height="auto"
    :pivotY="0.15"
>
    <div
        v-if="folderInDeletion"
        class="p-8"
    >
        <div class="text-red-500 font-bold mb-4">
            {{ $t("folderDeletionWarning", { folderName: folderInDeletion.name }) }}
            <br />
            {{
                $tc("folderDeletionItemsCount", itemsInFolderInDeletion, {
                    itemsInFolderInDeletion,
                })
            }}
        </div>

        <button
            class="button mr-2"
            @click="
                $emit('cancel')
                $modal.hide('deleteFolder')
            "
        >
            {{ $t("cancel") }}
        </button>
        <button
            class="button is-red"
            @click="$emit('confirm')"
        >
            {{ $t("confirmDeletion") }}
        </button>
    </div>
</Modal>
</template>

<script>
import { countItemsInHierarchy } from "@js/hierarchy"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "DeleteFolderModal",
    mixins: [PilotMixin],
    props: {
        folderInDeletion: Object,
    },
    computed: {
        itemsInFolderInDeletion() {
            return countItemsInHierarchy(this.folderInDeletion.nodes)
        },
    },
    i18n: {
        messages: {
            fr: {
                folderDeletionItemsCount:
                    "1 contenu sera déplacé vers la racine | {itemsInFolderInDeletion} contenus seront déplacés vers la racine",
                folderDeletionWarning:
                    'Êtes-vous sûr de vouloir supprimer le dossier "{folderName}" ?',
            },
            en: {
                folderDeletionItemsCount:
                    "1 content will be moved to the root | {itemsInFolderInDeletion} contents will be moved to the root",
                folderDeletionWarning:
                    'Are you sure you want to delete the folder "{folderName}" ?',
            },
        },
    },
}
</script>

<style lang="scss"></style>
