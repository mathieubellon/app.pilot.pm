<template>
<div class="FullCalendar">
    <div
        v-if="loadingInProgress.fetchItemsCalendar || loadingInProgress.fetchProjectsCalendar"
        class="FullCalendar__backdrop"
    >
        <Spinner />
    </div>

    <div
        class="FullCalendar__calendar"
        ref="calendar"
    ></div>

    <OffPanel name="confirmRescheduleTask">
        <div slot="offPanelTitle">
            {{ $t("confirmRescheduleTask") }}
        </div>
        <div
            v-if="rescheduleCalEvent"
            slot="offPanelBody"
        >
            {{
                $t("pleaseConfirmReschedule", {
                    title: rescheduleCalEvent.title,
                    date: rescheduleCalEvent.start.format("L"),
                })
            }}

            <hr />

            <SmartButtonSpinner
                name="updateTaskDeadline"
                :timeout="1500"
                @click="confirmRescheduleTask()"
            >
                {{ $t("yesConfirm") }}
            </SmartButtonSpinner>
            <button
                class="button hollow"
                @click="cancelRescheduleTask()"
            >
                {{ $t("cancel") }}
            </button>
        </div>
    </OffPanel>
</div>
</template>

<script>
/** Custom Full Calendar */
require("@js/lib/fullcalendar_yearview.2.2.7.js")
require("@js/lib/fullcalendar_yearview.2.2.7.css")

import _ from "lodash"
import $ from "jquery"
import { mapState, mapMutations, mapGetters, mapActions } from "vuex"
import moment from "moment"
import { serializeForQueryString } from "@js/queryString"
import Popper from "popper.js"
import PilotMixin from "@components/PilotMixin"

// A forked version of Fullcalendar is globally imported in index.js
// Because Forked version has YearView

export default {
    name: "FullCalendar",
    mixins: [PilotMixin],
    data: () => ({
        loading: true,
        // The calendar jquery element, on which we can call calendar.fullcalendar()
        calendar: null,
        currentPopper: null,
        rescheduleCalEvent: null, // Reschedule through drag'n'drop
        rescheduleRevertFunction: null, // When cancelling a drag'n'drop
    }),
    props: {
        header: {
            default: () => ({
                left: "prev,next today",
                center: "title",
                right: "year,month,basicWeek,basicDay",
                ignoreTimezone: false,
            }),
        },
        config: {
            type: Object,
            default: () => ({}),
        },
    },
    computed: {
        ...mapState("calendar", ["itemsApiSource"]),
        ...mapState("loading", ["loadingInProgress"]),
        ...mapGetters("calendar", ["eventSources"]),
        ...mapGetters("choices", ["getChoiceDisplay"]),
    },
    methods: {
        ...mapActions("calendar", ["fetchCalendarEvents", "updateTaskDeadline"]),
        getStartDate() {
            return _.get(this, "itemsApiSource.queryParamSerializer.params.start.0")
        },
        getDefaultConfig() {
            let initialDate = null
            let startDate = this.getStartDate()
            if (startDate) {
                startDate = moment(startDate)
                // If the start date is day 1 of the month, then we're already good t ogo
                if (startDate.date() == 1) {
                    initialDate = startDate
                }
                // else, we must go to the day 1 of the next month
                else {
                    initialDate = startDate.date(1).add(1, "months")
                }
            }

            let defaultConfig = {
                header: this.header,
                defaultView: "month",
                editable: false, // False by default for the projects, each task will override this
                eventStartEditable: true, // User can drag tasks around
                eventDurationEditable: false, // But not resize them
                eventLimit: true, // allow "more" link when too many events
                defaultDate: initialDate,
                // SUPER pour HM en V3.3.0 showNonCurrentDates: false,
                selectable: false,
                selectHelper: false,
                firstDay: 1,
                yearTitleFormat: "YYYY",
                columnFormat: {
                    month: "dddd",
                    week: "ddd DD/MM",
                    day: "dddd DD/MM",
                },
                eventSources: this.eventSources,
                // timeFormat: 'HH:mm',
                timeFormat: " ",
                eventMouseover: this.showPopper,
                eventMouseout: this.hidePopper,
                eventDragStart: this.hidePopper,
                eventDrop: this.requestRescheduleTask, // A task has been drag'n'droped

                eventDragStop: () => {},

                viewRender: (view, element) => {
                    // Each time FullCalendar render a new view we push start and end date in the api source.
                    this.itemsApiSource.setQuery({
                        ...this.itemsApiSource.query,
                        start: serializeForQueryString(view.start),
                        end: serializeForQueryString(view.end),
                    })
                },
                eventClick: (event, jsEvent) => {
                    this.hidePopper()
                    // If the ctrl key is used, then the user wants to open in a new tab,
                    // we must not use the router.
                    if (this.$router && !(jsEvent.ctrlKey || jsEvent.metaKey)) {
                        jsEvent.preventDefault()

                        if (event.type == "project") {
                            if (this.$store.state.sharing) {
                            } else {
                                this.$router.push({
                                    name: "projectDetail",
                                    params: {
                                        id: event.id,
                                    },
                                })
                            }
                        } else {
                            if (this.$store.state.sharing) {
                                this.$router.push({
                                    name: "sharedItem",
                                    params: {
                                        token: this.$store.state.sharing.token,
                                        itemId: event.item.id,
                                    },
                                })
                            } else {
                                this.$router.push({
                                    name: "itemDetail",
                                    params: {
                                        id: event.item.id,
                                    },
                                })
                            }
                        }
                    }
                },
            }

            if (this.$i18n.locale === "fr") {
                defaultConfig.lang = "fr"
                defaultConfig.locale = "fr"
                defaultConfig.months = "janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre".split(
                    "_",
                )
                defaultConfig.monthNames = [
                    "Janvier",
                    "Février",
                    "Mars",
                    "Avril",
                    "Mai",
                    "Juin",
                    "Juillet",
                    "Août",
                    "Septembre",
                    "Octobre",
                    "Novembre",
                    "Décembre",
                ]
                defaultConfig.monthNamesShort = [
                    "janv.",
                    "févr.",
                    "mars",
                    "avr.",
                    "mai",
                    "juin",
                    "juil.",
                    "août",
                    "sept.",
                    "oct.",
                    "nov.",
                    "déc.",
                ]
                defaultConfig.dayNames = [
                    "Dimanche",
                    "Lundi",
                    "Mardi",
                    "Mercredi",
                    "Jeudi",
                    "Vendredi",
                    "Samedi",
                ]
                defaultConfig.dayNamesShort = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"]
                defaultConfig.buttonText = {
                    today: "aujourd'hui",
                    day: "jour",
                    week: "semaine",
                    month: "mois",
                    year: "année",
                }
                defaultConfig.allDayHtml = "Toute la<br/>journée"
                defaultConfig.eventLimitText = "en plus"
            }

            return defaultConfig
        },
        reloadEventSources() {
            this.calendar.fullCalendar("removeEvents")
            for (let eventSource of this.eventSources) {
                this.calendar.fullCalendar("addEventSource", eventSource)
            }
        },
        showPopper(calEvent, browserEvent) {
            let content = []
            if (calEvent.type == "project") {
                let project = calEvent.project
                let category = project.category
                let categoryDisplay = category
                    ? '<span class="color-swatch" style="background-color: ' +
                      category.color +
                      '"></span>&nbsp' +
                      category.name
                    : "--"

                content.push(
                    '<div class="popOverEvent">',
                    '<div class="popOverEvent__title">' +
                        this.$t("project") +
                        " : " +
                        project.title +
                        "</div>",
                    "<div>" +
                        this.$t("start") +
                        " : " +
                        (project.start ? moment(project.start).format("D MMMM YYYY") : "-") +
                        "</div>",
                    "<div>" +
                        this.$t("end") +
                        " : " +
                        (project.end ? moment(project.end).format("D MMMM YYYY") : "-") +
                        "</div>",
                    "<div>" + this.$t("category") + " : " + categoryDisplay + "</div>",
                    "</div>",
                )
            } else if (calEvent.type == "task") {
                let task = calEvent.task,
                    item = calEvent.item
                /*let deadlineDisplay = moment(task.deadline).format(this.getDeadlineFormatting(item, task))
                let assigneesDisplay = task.assignees.map(user => '@'+ user.username).join('<br/>')*/
                let targetNames = item.targets.map((target) => target.name).join(", ")
                let channelNames = item.channels.map((channel) => channel.name).join(", ")

                content.push(
                    '<div class="popOverEvent">',
                    '<div class="popOverEvent__title">',
                    '<div class="popOverEvent__title__task">' + task.name + "</div>",
                    // '<div>' + this.$t('deadline') + ' : </div><div>' + deadlineDisplay + '</div>',
                    '<div class="popOverEvent__title__item">#' +
                        item.id +
                        " " +
                        item.title +
                        "</div>",
                    "</div>",
                    item.workflow_state
                        ? '<div style="font-size:0.9em;font-weight: bolder; color: ' +
                              item.workflow_state.color +
                              '">' +
                              this.$t("contentStatusIs") +
                              " " +
                              item.workflow_state.label +
                              "</div>"
                        : "",
                    item.project
                        ? "<div>" + this.$t("project") + " : " + item.project.name + "</div>"
                        : "",
                    channelNames
                        ? "<div>" + this.$t("channels") + " : " + channelNames + "</div>"
                        : "",
                    targetNames
                        ? "<div>" + this.$t("targets") + " : " + targetNames + "</div>"
                        : "",
                    item.language
                        ? "<div>" +
                              this.$t("language") +
                              " : " +
                              this.getChoiceDisplay("languagesChoices", item.language) +
                              "</div>"
                        : "",
                    "<div>" + this.$t("type") + " : " + item.item_type.name + "</div>",
                    "</div>",
                )
            }

            let html = `<div class="popper">${content.join(
                "",
            )}<div class="popper__arrow" x-arrow=""></div></div>`
            let contentElement = $(html).appendTo("body")
            this.currentPopper = new Popper(browserEvent.currentTarget, contentElement, {
                placement: "top",
                removeOnDestroy: true,
            })
        },
        hidePopper() {
            if (this.currentPopper) {
                this.currentPopper.destroy()
                this.currentPopper = null
            }
        },
        getDeadlineFormatting(item, task) {
            return "D MMMM YYYY"
        },
        requestRescheduleTask(calEvent, delta, revertFunction) {
            this.rescheduleCalEvent = calEvent
            this.rescheduleRevertFunction = revertFunction
            this.openOffPanel("confirmRescheduleTask")
        },
        confirmRescheduleTask() {
            this.updateTaskDeadline({
                taskId: this.rescheduleCalEvent.id,
                deadline: this.rescheduleCalEvent.start,
            })
                .then((response) => {
                    setTimeout(() => {
                        this.closeOffPanel("confirmRescheduleTask")
                    }, 1500)
                })
                .catch((error) => {
                    this.cancelRescheduleTask()
                })
        },
        cancelRescheduleTask() {
            this.rescheduleRevertFunction()
            this.closeOffPanel("confirmRescheduleTask")
        },
    },
    watch: {
        eventSources() {
            this.reloadEventSources()
        },
        "itemsApiSource.url"() {
            // Update the calendar view if necessary
            let startDate = this.getStartDate() || moment()
            let currentView = this.calendar.fullCalendar("getView")
            let isYearView = currentView.name == "year"
            if (startDate && !currentView.start.isSame(startDate) && !isYearView) {
                this.calendar.fullCalendar("gotoDate", startDate)
            }
            this.fetchCalendarEvents()
        },
    },
    mounted() {
        this.calendar = $(this.$refs.calendar)
        this.calendar.fullCalendar(_.defaultsDeep(this.config, this.getDefaultConfig()))
    },
    i18n: {
        messages: {
            fr: {
                confirmRescheduleTask: "Confirmer nouvelle date de tâche",
                pleaseConfirmReschedule: 'Vous allez déplacer la tâche "{title}" au {date}',
                yesConfirm: "Oui, confirmer",
                contentStatusIs: "Contenu actuellement en statut",
            },
            en: {
                confirmRescheduleTask: "Confirm task reschedule",
                pleaseConfirmReschedule: 'You asked to reschedule the task "{title}" to {date}',
                yesConfirm: "Yes, confirm",
                contentStatusIs: "Content currently in status",
            },
        },
    },
}
</script>

<style lang="scss">
.FullCalendar {
    margin-top: 1em;
}

.FullCalendar__calendar {
    width: 100%;
}

.FullCalendar .fc-view-container {
    background-color: #fff;
}

.FullCalendar__backdrop {
    background-color: rgba(250, 250, 250, 0.89);
    position: absolute;
    // Below Popper (100) and Offpanel (90) and topbar (50)
    z-index: 40;
    width: 100%;
    height: 100%;
    display: flex;
    //align-items: center;
    justify-content: center;
}
.popOverEvent {
    display: flex;
    flex-direction: column;
    padding: 1em;
    align-items: flex-start;
}
.popOverEvent__title {
    //align-self: center;
    font-weight: bolder;
    color: #1f2d3d;
    font-size: 1.15em;
    margin-bottom: 0.5em;
}
.popOverEvent__title__task {
    text-align: left;
}

.popOverEvent__title__item {
    color: #738a95;
}
</style>
