<script>
import TourMixin from "./TourMixin.vue"

// It could have been a little nicer with only extending the IntroJS steps property as a data property
// But it does not work (because in Popper?), and IntroJs does not find the data-tour attributes in page, so we will copy for each tour the whole methods object which is not DRY.
export default {
    extends: TourMixin,
    name: "DashboardTour",
    data: function () {
        return {
            getGuideSteps: () => [
                {
                    intro: this.$i18n.t("intro"),
                },
                {
                    element: document.querySelector("[data-tour='monitoring']"),
                    intro: this.$i18n.t("monitoring"),
                },
                {
                    element: document.querySelector("[data-tour='tasks']"),
                    intro: this.$i18n.t("tasks"),
                    position: "left",
                },
                {
                    element: document.querySelector("[data-tour='notifications']"),
                    intro: this.$i18n.t("notifications"),
                    position: "left",
                },

                {
                    intro: this.$i18n.t("outro"),
                },
            ],
            tourName: "dashboardTour",
        }
    },
    i18n: {
        messages: {
            fr: {
                intro:
                    "<h2>Découvrez votre tableau de bord en quelques secondes</h2><div>Circulez facilement entre les étapes du guide avec les flêches droite et gauche de votre clavier</div>",
                monitoring:
                    "<h2>Le monitoring</h2>Vous pouvez ajouter ici des blocs d'infos à votre convenance pour surveiller les contenus ou projets qui vous intéressent. <p>Visible par vous seulement.</p>",
                notifications:
                    "<h2>Les notifications</h2><p>Quand un membre de l'équipe vous mentionnera dans un commentaire la notification apparaitra ici</p>",
                outro:
                    " <img src=\"/static/img/guides/bravo.png\" /><h2>Bravo ! Ce guide est terminé</h2> <a class='moreToursLink'>D'autres guides plus détaillés</a> sont à votre disposition dans votre menu utilisateur",
                tasks:
                    "<h2>Les tâches</h2>A chaque contenu peut être associé une ou plusieurs tâches. <p>Chaque tâche aura un ou des responsables et une date de rendu.</p> <p>Celles qui vous seront assignées apparaitront ici.</p>",
                startTour: "Guide Tableau de bord",
                next: "suivant",
                previous: "précédent",
                done: "Terminé",
            },
            en: {
                intro:
                    "<h2>Discover your dashboard in a few seconds</h2><div>Circulate easily between the steps of the guide with the right and left arrows of your keyboard</div>",
                monitoring:
                    "<h2>Monitoring</h2>You can add info blocks here at your convenience to monitor the content or projects that interest you. <p>Visible by you only.</p>",
                notifications:
                    "<h2>Notifications</h2>When a team member mentions you in a comment the notification will appear here",
                outro:
                    " <img src=\"/static/img/guides/bravo.png\" /><h2>Bravo ! This guide is completed</h2> <a class='moreToursLink'>Other more detailed guides</a> are available in your user menu",
                tasks:
                    "<h2>Tasks</h2>A each content can be associated with one or more tasks. <p>Each task will have one or more responsible team member and a due date.</p> <p>These that will be assigned to you will appear here.</p>",
                startTour: "Dashboard Guide",
                next: "next",
                previous: "previous",
                done: "Done",
            },
        },
    },
}
</script>
