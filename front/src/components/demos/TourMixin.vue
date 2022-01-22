<template>
<a
    v-if="buttonVisible"
    class="menu-item"
    @click.prevent="startTour()"
>
    {{ $t("startTour") }}
</a>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import introJs from "intro.js"

let autoStartDone = false

export default {
    name: "TourMixin",
    props: {
        buttonVisible: {
            type: Boolean,
            default: false,
        },
    },
    data: function () {
        return {
            getGuideSteps: () => [],
            tourName: null,
        }
    },
    computed: {
        tourNameInQueryParam() {
            return this.$route && _.has(this.$route.query, this.tourName)
        },
        autoStart() {
            return this.tourNameInQueryParam
        },
    },
    methods: {
        ...mapMutations("offPanel", ["openOffPanel", "closeOffPanel"]),
        cleanUrl() {
            if (this.$router) {
                this.$router.replace("/")
            }
        },
        startTour() {
            this.closeOffPanel("tours")
            let intro = introJs.introJs()
            intro.setOptions({
                showStepNumbers: false,
                showProgress: true,
                nextLabel: this.$i18n.t("next"),
                prevLabel: this.$i18n.t("previous"),
                skipLabel: this.$i18n.t("cancel"),
                doneLabel: this.$i18n.t("done"),
                steps: this.getGuideSteps(),
            })
            intro.start()
            intro.onexit(() => {
                this.cleanUrl()
            })

            $(".introjs-tooltipReferenceLayer").on("click", ".moreToursLink", () => {
                intro.exit()
                this.openOffPanel("tours")
            })
        },
    },
    created: function () {
        // myPermissions.is_admin
        // window.pilot.user.firstLogin
        // window.pilot.desk.hasItems
        // window.pilot.desk.hasProjects
        //
        //
        // Comme users.me est récupéré en asynchrone, ca peut valoir le coup de plutôt checker window.pilot.user.permission qui est disponible immédiatement.
        // On peut éventuellement ajouter window.pilot.user.isAdmin pour être un poil plus clean.
        if (this.autoStart && !autoStartDone) {
            let waitReady = setInterval(() => {
                // Every step that declare an element property must have the element fully loaded before we can proceed
                if (
                    _.some(
                        this.getGuideSteps().map(
                            (step) => _.has(step, "element") && !Boolean(step.element),
                        ),
                    )
                )
                    return

                // Ok, all elements are now present on the page, we can start the tour
                autoStartDone = true
                clearInterval(waitReady)
                this.startTour()
            }, 200)
        }
    },
    beforeDestroy() {
        $(".introjs-tooltipReferenceLayer").off("click")
    },
}
</script>

<style lang="scss">
@import url("~intro.js/introjs.css");
@import "~@sass/colors.scss";

.introjs-tooltiptext {
    font-size: 1.3em;
    line-height: 1.2em;
}

.introjs-helperLayer {
    background-color: rgb(255, 255, 255) !important;
}

.introjs-tooltip {
    background-color: white;
    color: $gray-dark;
    padding: 2em;
    h2 {
        color: $dark;
        margin-top: 0;
        margin-bottom: 0.5em;
        font-size: 1.3em;
        line-height: 1.1em;
    }
    .button {
        margin-top: 1em;
    }

    .introjs-tooltipbuttons {
        .introjs-button {
            font: inherit;
        }
    }
}

// Leave this in peace !
// I still can't succeed at override attribute in svg from css. So hard
// So I rely on hacks for, in this example, have this main menu element (which has white strokes)
// to be still  visible on white background
.MainMenu_element.has-tooltip.introjs-showElement.introjs-relativePosition {
    background-color: #2196f3;
}
</style>
