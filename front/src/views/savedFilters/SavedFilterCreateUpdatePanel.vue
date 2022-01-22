<template>
<OffPanel
    name="savedFilterCreateUpdate"
    @opened="onOpen"
>
    <div slot="offPanelTitle">{{ isInternalSharedSavedFilter ? $t("copy") : $t("save") }}</div>
    <div slot="offPanelBody">
        <BaseForm
            v-if="createdSavedFilter === null"
            :errorText="$t('savedFilterCreationError')"
            :model="savedFilter"
            :saveUrl="urls.savedFilters"
            :successText="$t('savedFilterCreated')"
            :vuelidate="$v.savedFilter"
            @cancel="closeForm"
            @saved="onSavedFilterSaved"
        >
            <FormField
                :schema="{
                    type: 'char',
                    label: $t('title'),
                    placeholder: $t('title'),
                }"
                v-model.trim="savedFilter.title"
                :vuelidate="$v.savedFilter.title"
            />

            <div
                v-if="isCalendar && !savedFilter.id"
                class="form__field"
            >
                <label>
                    <ToggleButton
                        v-model="savedFilter.is_sliding_calendar"
                        :labels="true"
                        :sync="true"
                    />
                    {{ $t("isSlidingCalendar") }}
                </label>
            </div>

            <div
                v-if="isCalendar && !savedFilter.id"
                class="form__field"
            >
                <label>
                    <ToggleButton
                        v-model="savedFilter.display_projects"
                        :labels="true"
                        :sync="true"
                    />
                    {{ $t("displayProjects") }}
                </label>
            </div>

            <div
                v-if="isCalendar && !savedFilter.id"
                class="form__field"
            >
                <label>
                    <ToggleButton
                        v-model="savedFilter.display_tasks"
                        :labels="true"
                        :sync="true"
                    />
                    {{ $t("displayTasks") }}
                </label>
            </div>

            <div
                v-if="isCalendar && !savedFilter.id"
                class="form__field"
            >
                <label>
                    <ToggleButton
                        :labels="true"
                        :sync="true"
                        :value="!savedFilter.display_all_tasks"
                        @input="savedFilter.display_all_tasks = !savedFilter.display_all_tasks"
                    />
                    {{ $t("editorialCalendar") }}
                </label>
            </div>

            <div
                v-if="isCalendar && !savedFilter.id"
                class="form__field"
            >
                <label>
                    <ToggleButton
                        :labels="true"
                        :sync="true"
                        :value="savedFilter.display_all_tasks"
                        @input="savedFilter.display_all_tasks = !savedFilter.display_all_tasks"
                    />
                    {{ $t("allTasksCalendar") }}
                </label>
            </div>
        </BaseForm>

        <div v-else>
            <p>Le filtre "{{ createdSavedFilter.title }}" a été créée avec succès</p>
            <a
                class="button hollow expanded"
                @click="closeForm"
            >
                Fermer le panel
            </a>
        </div>
    </div>
</OffPanel>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { required } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"

import { ToggleButton } from "vue-js-toggle-button"

const EMPTY_SAVED_FILTER = {
    type: null,
    title: "",
    query: "",
    display_projects: false,
    display_tasks: false,
    display_all_tasks: false,
    is_sliding_calendar: true,
}

export default {
    name: "SavedFilterCreateUpdatePanel",
    mixins: [PilotMixin],
    components: {
        ToggleButton,
    },
    props: {
        isCalendar: Boolean,
        filtersQueryString: String,
    },
    data: () => ({
        savedFilter: _.clone(EMPTY_SAVED_FILTER),
        createdSavedFilter: null,
    }),
    validations: {
        savedFilter: {
            title: { required },
        },
    },
    computed: {
        ...mapState("users", ["me"]),
        ...mapGetters("savedFilter", [
            "isFilterTabOpen",
            "selectedSavedFilter",
            "isInternalSharedSavedFilter",
        ]),
    },
    methods: {
        ...mapMutations("savedFilter", ["appendSavedFilter", "updateSavedFilterInList"]),
        onSavedFilterSaved(savedFilter) {
            // On update, update the filter in the tab
            if (this.savedFilter.id) {
                this.updateSavedFilterInList(savedFilter)
                this.closeForm()
            }
            // On create, display the new filter in the tabs
            else {
                this.createdSavedFilter = savedFilter
                this.savedFilter.title = ""
                this.appendSavedFilter(savedFilter)
                // Navigate to the filter tab
                let routeName = savedFilter.type == "list" ? "itemList-filter" : "calendar-filter"
                this.$router.push({ name: routeName, params: { id: savedFilter.id } })
            }
        },
        closeForm() {
            this.closeOffPanel("savedFilterCreateUpdate")
        },
        onOpen() {
            this.savedFilter = _.clone(EMPTY_SAVED_FILTER)
            this.createdSavedFilter = null

            // If we're on a filter tab
            if (this.isFilterTabOpen) {
                // If it's an internal shared filter, we can copy it
                if (this.isInternalSharedSavedFilter) {
                    this.savedFilter.title = this.selectedSavedFilter.title
                }
                // Else, this form is for editing the existing filter
                else {
                    _.assign(this.savedFilter, this.selectedSavedFilter)
                }
            }

            this.savedFilter.type = this.isCalendar ? "calendar" : "list"
            this.savedFilter.query = this.filtersQueryString
            this.savedFilter.display_projects = this.me.config_calendar.displayProjects
            this.savedFilter.display_tasks = this.me.config_calendar.displayTasks
            this.savedFilter.display_all_tasks = this.me.config_calendar.displayAllTasks
        },
    },
    i18n: {
        messages: {
            fr: {
                allTasksCalendar: "Calendrier suivi des tâches",
                displayProjects: "Afficher les projets",
                displayTasks: "Afficher les contenus",
                editorialCalendar: "Calendrier de publication",
                isSlidingCalendar: "Calendrier glissant",
                savedFilterCreated: "Filtre sauvegardé",
                savedFilterCreationError: "Erreur, filtre non sauvegardé",
            },
            en: {
                allTasksCalendar: "Tasks calendar",
                displayProjects: "Display projects",
                displayTasks: "Display items",
                editorialCalendar: "Publication calendar",
                isSlidingCalendar: "Sliding calendar",
                savedFilterCreated: "Filter saved",
                savedFilterCreationError: "Error, filter not saved",
            },
        },
    },
}
</script>
