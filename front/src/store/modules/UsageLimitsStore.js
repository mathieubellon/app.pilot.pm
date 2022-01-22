import _ from "lodash"
import { EVENTS, mapEvents } from "@js/events"

export default {
    namespaced: true,
    state: {
        // Clone to prevent memory leak incurred by a top-level reactive object.
        usageLimits: _.cloneDeep(_.get(window, "pilot.desk.usageLimits", {})),
    },
    mutations: {
        incrementUsage(state, usageLimitName) {
            state.usageLimits[usageLimitName].current_usage += 1
        },
        decrementUsage(state, usageLimitName) {
            state.usageLimits[usageLimitName].current_usage -= 1
        },
    },
    getters: {
        usageLimitReached: (state) => (usageLimitName) => {
            let usageLimit = state.usageLimits[usageLimitName]
            if (!usageLimit) {
                return true
            }
            // Unlimited usage
            if (usageLimit.max_usage === -1) {
                return false
            }
            return usageLimit.current_usage >= usageLimit.max_usage
        },
        allowAdvancedFeatures: (state) => {
            return _.get(window, "state.usageLimits.advanced_features.current_usage")
        },
    },
    actions: {
        ...mapEvents({
            [EVENTS.itemCreated]({ commit }) {
                commit("incrementUsage", "items")
            },

            [EVENTS.itemTrashed]({ commit }) {
                commit("decrementUsage", "items")
            },

            [EVENTS.projectCreated]({ commit }) {
                commit("incrementUsage", "projects")
            },

            [EVENTS.projectClosed]({ commit }) {
                commit("decrementUsage", "projects")
            },

            [EVENTS.projectDeleted]({ commit }, project) {
                if (project.state == "active") {
                    commit("decrementUsage", "projects")
                }
            },

            [EVENTS.userInvited]({ state, commit }) {
                commit("incrementUsage", "users")
                state.usageLimits.users.extra.invitations += 1
            },

            [EVENTS.userDeinvited]({ state, commit }) {
                commit("decrementUsage", "users")
                state.usageLimits.users.extra.invitations -= 1
            },

            [EVENTS.userReactivated]({ state, commit }) {
                commit("incrementUsage", "users")
                state.usageLimits.users.extra.users += 1
            },

            [EVENTS.userDeactivated]({ state, commit }) {
                commit("decrementUsage", "users")
                state.usageLimits.users.extra.users -= 1
            },
        }),
    },
}
