import _ from "lodash"
import { EVENTS, mapEvents } from "@js/events"

export default {
    namespaced: true,
    state: {
        choices: {
            channels: [],
            items: [],
            languages: [],
            projects: [],
            targets: [],
            users: [],
        },
    },
    mutations: {
        setChoices(state, { choices, choicesName }) {
            state.choices[choicesName] = choices
        },
        addOneChoiceInstance(state, { choicesName, instance }) {
            state.choices[choicesName].unshift(instance)
        },
        updateOneChoiceInstance(state, { choicesName, instance }) {
            // Warning : won't work for language
            state.choices[choicesName] = state.choices[choicesName].map((oldChoice) =>
                oldChoice.id == instance.id ? instance : oldChoice,
            )
        },
        removeOneChoiceInstance(state, { choicesName, instance }) {
            // Warning : won't work for language
            state.choices[choicesName] = state.choices[choicesName].filter(
                (choice) => choice.id != instance.id,
            )
        },
    },
    getters: {
        itemChoicesById(state) {
            return _.keyBy(state.choices.items, "id")
        },

        channelChoices(state) {
            return state.choices.channels.map((channel) => ({
                value: channel.id,
                label: channel.name,
            }))
        },

        channelChoicesById(state) {
            return _.keyBy(state.choices.channels, "id")
        },

        languagesChoices(state) {
            return state.choices.languages.map((language) => ({
                value: language.name,
                label: language.label,
            }))
        },
        projectChoices(state) {
            return state.choices.projects.map((project) => ({
                value: project.id,
                label: project.name,
            }))
        },
        targetChoices(state) {
            return state.choices.targets.map((target) => ({ value: target.id, label: target.name }))
        },
        taskGroupChoices(state, getters, rootState) {
            return rootState.taskGroup.taskGroups.map((taskGroup) => ({
                value: taskGroup.id,
                label: taskGroup.name,
            }))
        },
        usersChoices(state) {
            return state.choices.users.map((user) => ({
                value: user.id,
                label: "@" + user.username,
            }))
        },
        workflowStateChoices(state, getters, rootState) {
            return rootState.workflow.workflowStates.map((workflowState) => ({
                value: workflowState.id,
                label: workflowState.label,
            }))
        },

        getChoiceDisplay: (state, getters) => (choicesName, choiceValue) => {
            for (let { value, label } of getters[choicesName]) {
                if (choiceValue == value) {
                    return label
                }
            }
            return null
        },
    },
    actions: {
        /***********************
         * Listeners to store events
         ************************/

        ...mapEvents({
            [EVENTS.projectCreated]({ commit }, project) {
                commit("addOneChoiceInstance", {
                    choicesName: "projects",
                    instance: project,
                })
            },

            [EVENTS.projectUpdated]({ commit }, project) {
                commit("updateOneChoiceInstance", {
                    choicesName: "projects",
                    instance: project,
                })
            },

            [EVENTS.projectClosed]({ commit }, project) {
                commit("removeOneChoiceInstance", {
                    choicesName: "projects",
                    instance: project,
                })
            },

            [EVENTS.projectDeleted]({ commit }, project) {
                commit("removeOneChoiceInstance", {
                    choicesName: "projects",
                    instance: project,
                })
            },

            [EVENTS.itemCreated]({ commit }, item) {
                commit("addOneChoiceInstance", {
                    choicesName: "items",
                    instance: item,
                })
            },

            [EVENTS.itemUpdated]({ commit }, item) {
                commit("updateOneChoiceInstance", {
                    choicesName: "items",
                    instance: item,
                })
            },

            [EVENTS.itemTrashed]({ commit }, item) {
                commit("removeOneChoiceInstance", {
                    choicesName: "items",
                    instance: item,
                })
            },

            [EVENTS.channelCreated]({ commit }, channel) {
                commit("addOneChoiceInstance", {
                    choicesName: "channels",
                    instance: channel,
                })
            },

            [EVENTS.channelUpdated]({ commit }, channel) {
                commit("updateOneChoiceInstance", {
                    choicesName: "channels",
                    instance: channel,
                })
            },

            [EVENTS.channelClosed]({ commit }, channel) {
                commit("removeOneChoiceInstance", {
                    choicesName: "channels",
                    instance: channel,
                })
            },

            [EVENTS.channelDeleted]({ commit }, channel) {
                commit("removeOneChoiceInstance", {
                    choicesName: "channels",
                    instance: channel,
                })
            },

            [EVENTS.targetCreated]({ commit }, target) {
                commit("addOneChoiceInstance", {
                    choicesName: "targets",
                    instance: target,
                })
            },

            [EVENTS.targetUpdated]({ commit }, target) {
                commit("updateOneChoiceInstance", {
                    choicesName: "targets",
                    instance: target,
                })
            },

            [EVENTS.targetDeleted]({ commit }, target) {
                commit("removeOneChoiceInstance", {
                    choicesName: "targets",
                    instance: target,
                })
            },

            [EVENTS.userReactivated]({ commit }, user) {
                commit("addOneChoiceInstance", {
                    choicesName: "users",
                    instance: user,
                })
            },

            [EVENTS.userDeactivated]({ commit }, user) {
                commit("removeOneChoiceInstance", {
                    choicesName: "users",
                    instance: user,
                })
            },
        }),
    },
}
