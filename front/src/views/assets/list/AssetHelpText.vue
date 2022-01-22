<template>
<div class="help-text">
    <div class="help-text-title">
        <Icon
            class="help-text-icon"
            name="Asset"
        />
        <span>{{ $t("emptyState") }}</span>
    </div>
    <div class="help-text-content">
        {{ $t("helpTextContent") }}
    </div>
    <button class="button is-blue startUpload">
        {{ $t("addButton") }}
    </button>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "AssetHelpText",
    mixins: [PilotMixin],
    i18n: {
        messages: {
            fr: {
                emptyState: "Aucun fichier",
                addButton: "Ajouter un fichier",
                helpTextContent:
                    "Les fichiers sont des documents image, vidéo, audio, PDF ou Microsoft Office. Ils sont \"liés\" aux contenus et peuvent être stockés en un seul endroit, dans ce dépôt. Il n'y a pas de limite de taille pour l'upload",
            },
            en: {
                emptyState: "No file",
                addButton: "Add file",
                helpTextContent:
                    'Files are images, videos, audios, PDF or Microsoft Office documents. They are "linked" to one or multiple contents. No size limit for upload',
            },
        },
    },
}
</script>
