<script>
import TourMixin from "./TourMixin.vue"

export default {
    extends: TourMixin,
    name: "GlobalTour",

    data: function () {
        return {
            getGuideSteps: () => [
                {
                    intro: this.$i18n.t("intro"),
                },
                {
                    element: document.querySelector("[data-tour='dashboardMainMenu']"),
                    intro: this.$i18n.t("dashboard"),
                },
                {
                    element: document.querySelector("[data-tour='itemsMainMenu']"),
                    intro:
                        this.$i18n.t("items") +
                        '<p><small><italic><a href="/items/active?tour">' +
                        this.$i18n.t("guideList") +
                        "</a></italic></small></p>",
                },
                {
                    element: document.querySelector("[data-tour='projectsMainMenu']"),
                    intro: this.$i18n.t("projects"),
                },
                {
                    element: document.querySelector("[data-tour='calendarsMainMenu']"),
                    intro: this.$i18n.t("calendars"),
                    position: "right",
                },
                {
                    element: document.querySelector("[data-tour='channelsMainMenu']"),
                    intro: this.$i18n.t("channels"),
                },
                {
                    element: document.querySelector("[data-tour='assetsMainMenu']"),
                    intro: this.$i18n.t("assets"),
                },
                {
                    element: document.querySelector("[data-tour='settingsMainMenu']"),
                    intro: this.$i18n.t("settings"),
                },
                {
                    element: document.querySelector("[data-tour='userbar']"),
                    intro: this.$i18n.t("userbar"),
                },
                {
                    intro: this.$i18n.t("outro"),
                },
            ],
            tourName: "globalTour",
        }
    },
    computed: {
        autoStart() {
            return this.tourNameInQueryParam || window.pilot.user.firstLogin
        },
    },
    i18n: {
        messages: {
            fr: {
                assets:
                    "<h2>Les fichiers liés</h2> <div> Les fichiers liés à vos contenus (vidéos, images, audios, PDF etc ..) sont centralisés ici pour pouvoir être associés à nouveau vers plusieurs autres contenus et mis à jour en un seul lieu.</div>",
                calendars:
                    " <h2>Le calendrier des tâches</h2><div>Planifiez toutes les tâches liées aux contenus dans des calendriers d'équipe ou privés. <p>Configurez des calendriers éditoriaux pour toute l'équipe ou juste pour vous avec les validations que vous devez faire sur les 7 prochains jours par exemple</p></div>",
                channels:
                    "<h2>Les canaux</h2> <div> C'est la représentation de vos supports sur lesquels seront diffusés les contenus. <p>Il peut s'agir d'un magazine, d'un évènement ou du plan de site hiérarchisé de votre Intranet</p></div>",
                dashboard:
                    "<h2>Votre tableau de bord</h2> <div>Retrouvez ici les éléments essentiels de votre activité sur ce desk. <p>Ce tableau de bord est uniquement visible par vous même.</p></div>",
                done: "Terminé",
                guideList: "Ouvrir le guide détaillé des contenus",
                intro:
                    "<h2>Découvrez votre desk en quelques minutes</h2><div>Circulez facilement entre les écrans de ce guide grâce aux flêches droite et gauche de votre clavier.</div>",
                items:
                    "<h2>Les contenus</h2> <div>Tous les contenus sont disponibles ici pour toute l'équipe. <p>Des fonctions avancées vous permettent de filtrer la liste générale et créer vos propres listes privées.</p></div>",
                next: "Suivant",
                outro:
                    " <img src=\"/static/img/guides/bravo.png\" /><h2>Bravo ! Ce guide d'introduction est terminé</h2> <a class='moreToursLink'>D'autres guides plus détaillés</a> sont à votre disposition dans votre menu utilisateur <p> Nous sommes toujours joignables sur support@pilot.pm pour toutes questions.</p>",
                previous: "Précédent",
                projects:
                    "<h2>Les projets</h2> <div>Utilisez les pour regrouper des contenus par finalité ou thématique. <p>Vous pouvez assigner des responsables, des descriptions ou des ordres de priorité à un projet</p></div>",
                settings:
                    "<h2>Les paramètres de desk</h2> <div>Toutes les options de configuration du desk sont ici (gestion de l'équipe, des gabarits, des workflows, etc ..).<p> Accessible uniquement aux admins.</p></div>",
                startTour: "Interface générale",
                userbar:
                    "<h2>Votre menu utilisateur</h2>Retrouvez ici vos notifications, tâches en cours, moteur de recherche global et les accès à vos outils de compte",
            },
            en: {
                assets:
                    "<h2>Linked files</h2> <div> Files related to your contents (videos, images, audio, PDF etc...) are centralized here to be able to be associated again to several other contents and updated in a single place.</div>",
                calendars:
                    "<h2>Tasks calendar</h2> <div>Plan all tasks related to contents in team or private calendars. <p>Configure editorial calendars for the whole team or just for you with the validations you need to do over the next 7 days for example</p></div>",
                channels:
                    "<h2>Channels</h2> <div> This is the representation of your media on which the contents will be distributed. <p>It can be a magazine, an event or the hierarchical site map of your Intranet</p></div>",
                dashboard:
                    "<h2>Your dashboard</h2> <div>Find here the essential elements of your activity on this desk. <p>This dashboard is only visible to yourself.</p></div>",
                done: "Done",
                guideList: "Open the detailed content guide",
                intro:
                    "<h2>Discover your desk</h2><div>Circulate easily between the screens of this guide with the right and left arrows of your keyboard.</div>",
                items:
                    "<h2>Content</h2> <div>All content is available here for the whole team. <p>Advanced functions allow you to filter the general list and create your own private lists.</p></div>",
                next: "Next",
                outro:
                    " <img src=\"/static/img/guides/bravo.png\" /><h2>Bravo ! This introductory guide is finished</h2> <a class='moreToursLink'>Other more detailed guides</a> are available in your user menu <p> We are always available on support@pilot.pm for any questions.</p>",
                previous: "Previous",
                projects:
                    "<h2>Projects</h2> <div>Use them to group content by purpose or theme.<p>You can assign managers, descriptions or priorities to a project</p></div>",
                settings:
                    "<h2>Desk settings</h2> <div>All desk configuration options are here (team management, content templates, workflows, etc...).<p>Accessible only to admins.</p></div>",
                startTour: "General interface",
                userbar:
                    "<h2>Your user menu</h2>Find here your notifications, current tasks, global search engine and access to your account tools",
            },
        },
    },
}
</script>
