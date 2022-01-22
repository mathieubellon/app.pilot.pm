<template>
<div class="help-text">
    <template v-if="currentRouteName == 'projectList-idea'">
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="ProjectSuggested"
            />
            <span>{{ $t("idea.emptyState") }}</span>
        </div>
        <div class="help-text-content">
            {{ $t("idea.helpTextContent") }}
        </div>
        <button
            class="button is-blue"
            @click.prevent="openOffPanel('addIdeaProjectForm')"
        >
            {{ $t("idea.addButton") }}
        </button>
    </template>

    <template v-if="currentRouteName == 'projectList-active'">
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="Project"
            />
            <span>{{ $t("active.emptyState") }}</span>
        </div>
        <div class="help-text-content">
            {{ $t("active.helpTextContent") }}
        </div>
        <button
            class="button is-blue"
            @click.prevent="openOffPanel('addActiveProjectForm')"
        >
            {{ $t("active.addButton") }}
        </button>
    </template>

    <template v-if="currentRouteName == 'projectList-closed'">
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="ProjectClosed"
            />
            <span>{{ $t("closed.emptyState") }}</span>
        </div>
        <div class="help-text-content">
            {{ $t("closed.helpTextContent") }}
        </div>
    </template>
</div>
</template>

<script>
import { mapState, mapMutations, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ProjectHelpText",
    mixins: [PilotMixin],
    i18n: {
        messages: {
            fr: {
                idea: {
                    emptyState: "Aucun projet proposé",
                    addButton: "Ajouter une proposition de projet",
                    helpTextContent:
                        "Les brouillons peuvent être discutés et modifiés avant d'être validés par un admin. Une fois validé le projet passe en production et devient 'actif' (il peut être affiché dans un calendrier, servir à filtrer une liste, ..).",
                },
                active: {
                    emptyState: "Aucun projet",
                    addButton: "Ajouter un projet",
                    helpTextContent:
                        "Regroupez vos contenus dans un projet (refonte de site, magazine, évènement, ..)",
                },
                closed: {
                    emptyState: "Aucun projet fermé",
                    helpTextContent:
                        "Les projets fermés n'apparaissent plus dans les calendriers ou les filtres de liste. Ils peuvent être ré-ouverts et redevenir 'actifs'",
                },
            },
            en: {
                idea: {
                    emptyState: "No project suggested",
                    addButton: "Add a project suggestion",
                    helpTextContent:
                        "Suggested projects can be discussed and edited before being validated by an admin. Once validated the project goes into production and becomes 'active' (it can be displayed in a calendar, used to filter a list, ..).",
                },
                active: {
                    emptyState: "No project",
                    addButton: "Add project",
                    helpTextContent:
                        "Group your content into a project (website redesign, magazine, event,...)",
                },
                closed: {
                    emptyState: "No closed project",
                    helpTextContent:
                        "Closed projects no longer appear in calendars or list filters. They can be re-opened and re-activated",
                },
            },
        },
    },
}
</script>
