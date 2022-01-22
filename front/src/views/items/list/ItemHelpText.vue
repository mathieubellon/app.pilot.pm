<template>
<div class="help-text">
    <div class="help-text-title">
        <Icon
            class="help-text-icon"
            name="Item"
        />
        <span>{{ $t("listIsEmpty") }}</span>
    </div>

    <div class="help-text-content text-lg">
        {{ $t("active.helpTextContent") }}
    </div>
    <a
        class="button is-blue"
        @click.prevent="openOffPanel('addItem')"
    >
        {{ $t("active.addButton") }}
    </a>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ItemHelpText",
    mixins: [PilotMixin],
    i18n: {
        messages: {
            fr: {
                active: {
                    emptyState: "Aucun contenu",
                    addButton: "Ajouter un contenu",
                    helpTextContent:
                        "Utilisez les contenus pour produire vos tweets, pages web, articles de magazines ou des documents encore plus complexes et personnalisés. Vous pourrez commenter, versionner, annoter ces éléments avant de les faire valider.",
                },
                filter: {
                    emptyState: "Aucun contenu dans le filtre",
                },
                trash: {
                    emptyState: "Aucun contenu à la corbeille",
                    helpTextContent:
                        "Lorsque vous supprimez un contenu nous l'ajoutons à cette liste. Il peut être restauré pour redevenir 'actif'",
                },
            },
            en: {
                active: {
                    emptyState: "No content",
                    addButton: "Add content",
                    helpTextContent:
                        "Use contents to produce your tweets, web pages, magazine articles or even more complex and personalized documents. You will be able to comment, version, annotate these elements before having them validated. ",
                },
                filter: {
                    emptyState: "No content in the filter",
                },
                trash: {
                    emptyState: "No content in trash",
                    helpTextContent:
                        "When you delete a content we will list it here. It can be restored and set as 'active' again",
                },
            },
        },
    },
}
</script>
