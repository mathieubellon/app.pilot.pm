<template>
<div class="TeamPicker">
    <div class="flex items-center">
        <VueFuse
            class="flex-grow"
            :defaultAll="true"
            :keys="['name']"
            :list="teams"
            :placeholder="$t('search')"
            :threshold="0.1"
            @result="onFuseResult"
        />
        <template v-if="multiple">
            <ButtonSpinner
                class="button is-small is-outlined mx-2"
                :disabled="pickedTeamsId.length == teams.length"
                :isLoading="loading && lastSelection == 'pickAll'"
                @click="pickAll"
            >
                {{ $t("selectAll") }}
            </ButtonSpinner>

            <ButtonSpinner
                class="button is-small is-outlined"
                :disabled="pickedTeamsId.length == 0"
                :isLoading="loading && lastSelection == 'unpickAll'"
                @click="unpickAll"
            >
                {{ $t("deselectAll") }}
            </ButtonSpinner>
        </template>
    </div>

    <div class="Picker__List">
        <div
            v-for="team in filteredTeams"
            class="Picker__ElementWrapper"
        >
            <div
                v-if="loading && lastSelection == team"
                class="Picker__Loader"
            >
                <BarLoader
                    color="#3182CE"
                    :loading="true"
                    :width="100"
                    widthUnit="%"
                />
            </div>
            <TeamPickerElement
                v-else
                :disabled="loading"
                :key="team.id"
                :picked="isPicked(team)"
                :team="team"
                @pick="onPick"
            />
        </div>
    </div>

    <div
        v-if="teams.length == 0"
        class="help-text"
    >
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="Users"
            />
            <span>{{ $t("noTeamYet") }}</span>
        </div>
        <SmartLink
            class="button is-blue"
            :to="urls.teamsApp.url"
        >
            {{ $t("createTeam") }}
        </SmartLink>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import PilotMixin from "@components/PilotMixin"

import TeamPickerElement from "./TeamPickerElement.vue"
import ButtonSpinner from "@components/ButtonSpinner"

export default {
    name: "TeamPicker",
    mixins: [PilotMixin],
    components: {
        TeamPickerElement,
        ButtonSpinner,
    },
    props: {
        multiple: Boolean,
        teams: Array,
        pickedTeam: Object,
        pickedTeamsId: Array,
        loading: Boolean,
    },
    data: () => ({
        filteredTeams: [],
        lastSelection: null,
    }),
    methods: {
        onFuseResult(filteredTeams) {
            this.filteredTeams = filteredTeams
        },
        onPick(team) {
            this.lastSelection = team
            if (this.multiple) {
                // Toggle value in array (https://gist.github.com/uhtred/ec64752a8e9c9b83922b3ebb36e3ac23)
                this.$emit("pick", _.xor(this.pickedTeamsId, [team.id]))
            } else {
                this.$emit("pick", team)
            }
        },
        pickAll() {
            this.lastSelection = "pickAll"
            this.$emit(
                "pick",
                this.teams.map((team) => team.id),
            )
        },
        unpickAll() {
            this.lastSelection = "unpickAll"
            this.$emit("pick", [])
        },
        isPicked(team) {
            if (this.multiple) {
                return _.includes(this.pickedTeamsId, team.id)
            } else {
                return this.pickedTeam && this.pickedTeam.id == team.id
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                createTeam: "Créer une équipe",
                noTeamYet: "Vous n'avez pas encore créé d'équipe",
            },
            en: {
                createTeam: "Create a team",
                noTeamYet: "You haven't created any team yet",
            },
        },
    },
}
</script>
