<script>
import TourMixin from "./TourMixin.vue"

// It could have been a little nicer with only extending the IntroJS steps property as a data property
// But it does not work (because in Popper?), and IntroJs does not find the data-tour attributes in page, so we will copy for each tour the whole methods object which is not DRY.
export default {
    extends: TourMixin,
    name: "ItemListTour",
    data: function () {
        return {
            getGuideSteps: () => [
                {
                    intro: this.$i18n.t("intro"),
                },
                {
                    element: document.querySelector("[data-tour='itemListTabs']"),
                    intro: this.$i18n.t("itemListTabs"),
                },
                {
                    element: document.querySelector("[data-tour='toolbar']"),
                    intro: this.$i18n.t("toolbar"),
                    position: "auto",
                },
                {
                    intro: this.$i18n.t("outro"),
                },
            ],
            tourName: "itemListTour",
        }
    },
    i18n: {
        messages: {
            fr: {
                done: "Terminé",
                intro:
                    "<h2>Les contenus</h2> Nous stockons ici tous vos contenus, sans limite de temps. <p>Tous les membres de l'équipe y ont accès pour rapidement trouver la dernière version du document dont ils ont besoin.</p>",
                itemListTabs:
                    '<h2>Onglets de statut</h2>Ils permettent d\'afficher des listes de contenu selon leur état. <p><strong>"Proposés"</strong> : Désigne les contenus en cours de réflexion au sein de l\'équipe. Ils ne sont pas en production</p><p><strong>"Actifs"</strong> : Contenus actuellement en production</p><p><strong>"Supprimés"</strong> : Contenus supprimés, conservés ici jusqu\'à ce qu\'un membre de l\'équipe les supprime définitivement. Les contenus supprimés ne comptent plus dans vos limites de compte</p><p><strong>"Vos filtres"</strong> : Filtres privés ou d\'équipe, permettent de gérer des listes personnalisées de contenus.</p>',
                next: "Suivant",
                outro:
                    " <img src=\"/static/img/guides/bravo.png\" /><h2>Bravo ! Ce guide d'introduction est terminé</h2> <a class='moreToursLink'>D'autres guides plus détaillés</a> sont à votre disposition dans votre menu utilisateur <p> Nous sommes toujours joignables sur support@pilot.pm pour toutes questions.</p>",
                previous: "Précédent",
                startTour: "Guide liste de contenus",
                toolbar:
                    "<h2>Le 'bigfilter'</h2> <p>Permet de faire une recherche plein texte simple (titre et body) ou de combiner des filtres pour obtenir des listes intelligentes de contenus. Ces listes intelligentes évoluent avec les contenus et peuvent être sauvegardées.</p>",
            },
            en: {
                done: "Done",
                intro:
                    "<h2>The contents</h2> We store all your contents here, without time limit. <p>All team members have access to it to quickly find the latest version of the document they need.</p>",
                itemListTabs:
                    '<h2>Status tabs</h2>They display content lists according to their status. <p><strong>"Proposed"</strong> : Refers to the content being thought within the team. They are not in production</p><p><strong>"Active"</strong> : Contents currently in production</p><p><strong>"Deleted"</strong> : Contents deleted, kept here until a team member permanently deletes them. Deleted content no longer counts within your account limits</p><p><strong>"Your filters"</strong> : Private or team filters, allow you to manage personalized lists of content.</p>',
                next: "Next",
                outro:
                    " <img src=\"/static/img/guides/bravo.png\" /><h2>Bravo ! This introductory guide is finished</h2> <a class='moreToursLink'>Other more detailed guides</a> are available in your user menu <p> We are always available on support@pilot.pm for any questions.</p>",
                previous: "Précédent",
                startTour: "Content list guide",
                toolbar:
                    "<h2>The 'bigfilter'</h2> <p>Permits a simple full text search (title and body) or to combine filters to obtain intelligent content lists. These smart lists evolve with the content and can be saved.</p>",
            },
        },
    },
}
</script>
