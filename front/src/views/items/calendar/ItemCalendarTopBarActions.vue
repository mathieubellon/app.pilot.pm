<template>
<Fragment>
    <Popper
        triggerElementName="PopperRef"
        triggerType="click"
    >
        <template #triggerElement>
            <a
                class="button"
                ref="PopperRef"
            >
                {{ $t("displayOptions") }}
                <!-- The empty span is required to correctly align with flex display -->
                <span>
                    <Icon
                        class="caret"
                        name="ChevronDown"
                    />
                </span>
            </a>
        </template>

        <template #content>
            <div class="ItemCalendar__displayOptions">
                <div class="menu-title">{{ $t("calendarDisplayPreferences") }}</div>
                <div class="menu-subtitle">
                    {{ $t(selectedSavedFilter ? "privateFilterVisibility" : "onlyVisibleByYou") }}
                </div>

                <label class="menu-item">
                    <ToggleButton
                        v-model="displayProjects"
                        class="toggle"
                        :labels="true"
                        :sync="true"
                    />
                    <div class="flex flex-col items-start">
                        <span>{{ $t("displayProjects") }}</span>
                        <span class="menu-item-description">
                            {{ $t("displayProjectsToolTip") }}
                        </span>
                    </div>
                </label>

                <label class="menu-item">
                    <ToggleButton
                        v-model="displayTasks"
                        class="toggle"
                        :labels="true"
                        :sync="true"
                    />
                    <div class="flex flex-col items-start">
                        <span>{{ $t("displayTasks") }}</span>
                        <span class="menu-item-description">
                            {{ $t("displayTasksToolTip") }}
                        </span>
                    </div>
                </label>

                <label class="menu-item">
                    <ToggleButton
                        class="toggle"
                        :labels="true"
                        :sync="true"
                        :value="!displayAllTasks"
                        @input="displayAllTasks = !displayAllTasks"
                    />
                    <div class="flex flex-col items-start">
                        <span>{{ $t("editorialCalendar") }}</span>
                        <span class="menu-item-description">
                            {{ $t("editorialCalendarToolTip") }}
                        </span>
                    </div>
                </label>

                <label class="menu-item">
                    <ToggleButton
                        class="toggle"
                        :labels="true"
                        :sync="true"
                        :value="displayAllTasks"
                        @input="displayAllTasks = !displayAllTasks"
                    />
                    <div class="flex flex-col items-start">
                        <span>{{ $t("allTasksCalendar") }}</span>
                        <span class="menu-item-description">
                            {{ $t("allTasksCalendarToolTip") }}
                        </span>
                    </div>
                </label>

                <label
                    v-if="currentRouteName == 'calendar-filter'"
                    class="menu-item"
                >
                    <ToggleButton
                        class="toggle"
                        :labels="true"
                        :sync="true"
                        :value="isSlidingCalendar"
                        @input="isSlidingCalendar = !isSlidingCalendar"
                    />
                    <div class="flex flex-col items-start">
                        <span>{{ $t("isSlidingCalendar") }}</span>
                        <span class="menu-item-description">
                            {{ $t("isSlidingCalendarToolTip") }}
                        </span>
                    </div>
                </label>
            </div>
        </template>
    </Popper>

    <!-- The span is required to prevent Vue error with component reuse -->
    <span v-if="currentRouteName == 'calendar-filter'">
        <SavedFilterActions />
    </span>
</Fragment>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { initialDataPromise } from "@js/bootstrap"
import PilotMixin from "@components/PilotMixin"
import { Fragment } from "vue-fragment"
import { ToggleButton } from "vue-js-toggle-button"

import SavedFilterActions from "@views/savedFilters/SavedFilterActions.vue"

function createTwoWayProperty(userConfigFieldPath, filterFieldName) {
    return {
        get() {
            if (userConfigFieldPath && this.currentRouteName != "calendar-filter") {
                return _.get(this.me, userConfigFieldPath)
            } else if (filterFieldName && this.currentRouteName == "calendar-filter") {
                return this.selectedSavedFilter[filterFieldName]
            }
        },
        set(value) {
            if (userConfigFieldPath && this.currentRouteName != "calendar-filter") {
                this.updateUserField({
                    fieldPath: userConfigFieldPath,
                    value: value,
                })
            } else if (filterFieldName && this.currentRouteName == "calendar-filter") {
                this.partialUpdateSavedFilter({
                    id: this.savedFilterId,
                    [filterFieldName]: value,
                })
            }
        },
    }
}

export default {
    name: "ItemCalendarTopBarActions",
    mixins: [PilotMixin],
    components: {
        Fragment,
        ToggleButton,

        SavedFilterActions,
    },
    computed: {
        ...mapState("users", ["me"]),
        ...mapGetters("savedFilter", ["selectedSavedFilter"]),
        displayTasks: createTwoWayProperty("config_calendar.displayTasks", "display_tasks"),
        displayProjects: createTwoWayProperty(
            "config_calendar.displayProjects",
            "display_projects",
        ),
        displayAllTasks: createTwoWayProperty(
            "config_calendar.displayAllTasks",
            "display_all_tasks",
        ),
        isSlidingCalendar: createTwoWayProperty(null, "is_sliding_calendar"),
    },
    methods: {
        ...mapActions("users", ["updateUserField", "partialUpdateUser"]),
        ...mapActions("savedFilter", ["partialUpdateSavedFilter"]),
    },
    created() {
        initialDataPromise.then((response) => {
            // Init the calendar config if it's empty
            if (_.isEmpty(this.me.config_calendar)) {
                this.partialUpdateUser({
                    config_calendar: {
                        displayTasks: true,
                        displayProjects: false,
                        displayAllTasks: false,
                    },
                })
            }
        })
    },
    i18n: {
        messages: {
            fr: {
                allTasksCalendar: "Calendrier suivi des tâches",
                allTasksCalendarToolTip: "Affiche toutes les tâches",
                calendarDisplayPreferences: "Préférences d'affichage du calendrier",
                displayOptions: "Affichage",
                displayProjects: "Afficher les projets",
                displayProjectsToolTip: "Affiche / Masque les projets",
                displayTasks: "Afficher les contenus",
                displayTasksToolTip: "Affiche / Masque les contenus",
                editorialCalendar: "Calendrier de publication",
                editorialCalendarToolTip: "Affiche uniquement les tâches de publication",
                filterByTokens:
                    "Filtrer les contenus par projet(s) et/ou canaux, tags, statuts de workflow, ..",
                isSlidingCalendar: "Calendrier glissant",
                isSlidingCalendarToolTip: "Se déplace pour toujours afficher la date du jour",
                onlyVisibleByYou: "Ces choix sont uniquement visible par vous",
                privateFilterVisibility: "Ces choix s'appliquent sur votre filtre privé",
            },
            en: {
                allTasksCalendar: "Tasks calendar",
                allTasksCalendarToolTip: "Show all tasks",
                calendarDisplayPreferences: "Preferences for calendar display",
                displayOptions: "Display",
                displayProjects: "Display projects",
                displayProjectsToolTip: "Show / Hide projects",
                displayTasks: "Display items",
                displayTasksToolTip: "Show / Hide items",
                editorialCalendar: "Publication calendar",
                editorialCalendarToolTip: "Display only publication tasks",
                filterByTokens:
                    "Filter content by project (s) and / or channels, tags, workflow status, .",
                isSlidingCalendar: "Sliding calendar",
                isSlidingCalendarToolTip: "Move the timeframe to always show today's date",
                onlyVisibleByYou: "Those choices are only visible by you",
                privateFilterVisibility: "These preferences are set on your private filter",
            },
        },
    },
}
</script>
