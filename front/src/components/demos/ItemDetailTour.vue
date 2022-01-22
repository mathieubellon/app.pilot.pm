<script>
import TourMixin from "./TourMixin.vue"
import OffPanel from "@components/OffPanel.vue"

// It could have been a little nicer with only extending the IntroJS steps property as a data property
// But it does not work (because in Popper?), and IntroJs does not find the data-tour attributes in page, so we will copy for each tour the whole methods object which is not DRY.
export default {
    extends: TourMixin,
    name: "ItemDetailTour",
    components: {
        OffPanel,
    },
    data: function () {
        return {
            getGuideSteps: () => [
                {
                    element: document.querySelector("[data-tour='itemInfos']"),
                    intro: this.$i18n.t("itemInfos"),
                },
                {
                    element: document.querySelector("[data-tour='itemVersions']"),
                    intro: this.$i18n.t("itemVersions"),
                },
                {
                    element: document.querySelector("[data-tour='itemComments']"),
                    intro: this.$i18n.t("itemComments"),
                },
                {
                    element: document.querySelector("[data-tour='itemTasks']"),
                    intro: this.$i18n.t("itemTasks"),
                },
                {
                    element: document.querySelector("[data-tour='itemLinkedFiles']"),
                    intro: this.$i18n.t("itemLinkedFiles"),
                },
                {
                    element: document.querySelector("[data-tour='itemShares']"),
                    intro: this.$i18n.t("itemShares"),
                },
                {
                    intro: this.$i18n.t("outro"),
                },
            ],
            tourName: "itemDetailTour",
        }
    },
    i18n: {
        messages: {
            fr: {
                done: "Terminé",
                next: "Suivant",
                outro:
                    " <img src=\"/static/img/guides/bravo.png\" /><h2>Bravo ! Ce guide d'introduction est terminé</h2> <a class='moreToursLink'>D'autres guides plus détaillés</a> sont à votre disposition dans votre menu utilisateur <p> Nous sommes toujours joignables sur support@pilot.pm pour toutes questions.</p>",
                previous: "Précédent",
                startTour: "Guide interface de contenu",
                itemInfos:
                    "<h2>Informations générales relatives au contenu</h2><ul><li>Le projet auquel le contenu est affecté</li> <li>Le canal où le contenu sera publié</li> <li>Les éventuels responsables du document</li> <li>Les contenus liés (dans le cas de traduction par exemple pour avoir une référence au “master” ou pour lier un brief au contenu rédigé)</li></ul>",
                itemVersions:
                    '<h2>Versions</h2><p>A chaque sauvegarde nous créons une “version mineure” (1.1, 1.2, etc ..) avec l’heure de la création et la référence à la personne ayant créé cette version.</p><p><strong>Différences</strong><br>Une “vue des différences” vous permet de savoir très facilement ce qui a été ajouté ou supprimée d’une version à l’autre</p><p>Exemple:<br><img src="/static/img/guides/diff.png" alt="vue des différences"></p>',
                itemComments:
                    '<h2>Commentaires</h2><p>Pour interpeller un membre de l\'équipe tapez "@" dans la zone de commentaire puis les premières lettres de son nom.<p>Vous pourrez discuter de l’évolution du document grâce à cette fonctionnalité.</p>',
                itemTasks:
                    "<h2>Tâches</h2>A chaque contenu vous pourrez affecter des tâches librement. Chacune de ces tâches aura une date de rendu et un ou plusieurs responsables. <p>Seule la tâche 'Publier' ne peut être supprimée.</p>",
                itemLinkedFiles:
                    "<h2>Fichiers liés</h2>Vous pouvez lier un ou plusieurs fichiers à votre contenu (sans limite de taille de document)",
                itemShares:
                    "<h2>Partages</h2>Partagez le document soit en lecture seule soit en lecture/écriture. <p>Ensuite vous pourrez intégrer les modifications faites par vos contacts au document</p>",
            },
            en: {
                done: "Done",
                next: "Next",
                outro:
                    " <img src=\"/static/img/guides/bravo.png\" /><h2>Bravo ! This introductory guide is finished</h2> <a class='moreToursLink'>Other more detailed guides</a> are available in your user menu <p> We are always available on support@pilot.pm for any questions.</p>",
                previous: "Précédent",
                startTour: "Content interface guide",
                itemInfos:
                    '<h2>General information about the content</h2><ul><li>The project to which the content is assigned </li> <li>The channel where the content will be published </li> <li>Responsibles for the document </li> <li>Linked content (in the case of translation, for example, to have a reference to the "master" or to link a brief to the written content)</li></ul>',
                itemVersions:
                    '<h2>Versions</h2><p> For each saving we create a "minor version" (1.1, 1.2, etc...) with the time of creation and the reference to the person who created this version.</p><p><strong>Differences</strong><br> A "difference view" makes it very easy to see what has been added or deleted from one version to another</p><p>Example:<br><img src="/static/img/guides/diff.png" alt="vue des différences"></p>',
                itemComments:
                    '<h2>Comments</h2>To call a team member type "@" in the comment box then the first letters of his name.<p>You can discuss the evolution of the document with this feature.</p>',
                itemTasks:
                    "<h2>Tasks</h2>You can freely assign tasks to each content. Each of these tasks will have a due date and one or more persons responsible. <p>Only the'Publish' task cannot be deleted.</p>",
                itemLinkedFiles:
                    "<h2>Linked files</h2>You can link one or more files to your content (without document size limit)",
                itemShares:
                    "<h2>Share</h2>Share the document either read-only or read/write.<p>Then you can integrate the modifications made by your contacts to the document</p>",
            },
        },
    },
}
</script>
