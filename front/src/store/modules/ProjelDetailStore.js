import _ from "lodash"
import Vue from "vue"
import urls from "@js/urls"
import { $httpX } from "@js/ajax.js"
import { LocalStorageWrapper } from "@js/localStorage.js"

import ActivityFeedStore from "@/store/modules/ActivityFeedStore.js"
import LinkedAssetsStore from "@/store/modules/LinkedAssetsStore.js"
import LinkedTasksStore from "@/store/modules/LinkedTasksStore.js"

import { EVENTS, mapEvents, dispatchEvent } from "@js/events"

let localSidebarHierarchyVisibility = new LocalStorageWrapper("Projel.sidebarHierarchyVisibility")

export default {
    namespaced: true,
    modules: {
        activityFeed: ActivityFeedStore,
        linkedAssets: LinkedAssetsStore,
        linkedTasks: LinkedTasksStore,
    },
    state: {
        projel: {},
        itemsCount: "?",
        // Keep track of fields that are currently being saved
        // {fieldName : true/false}
        fieldsCurrentlyUpdating: {},
        isNameInEdition: false,
        lastFetchProjelPromise: null,
        sidebarHierarchyVisibility: localSidebarHierarchyVisibility.get() || {},
    },
    mutations: {
        setProjel(state, projel) {
            state.projel = projel
            state.itemsCount = projel.items_count
        },
        setItemsCount(state, itemsCount) {
            state.itemsCount = itemsCount
        },
        startFieldsCurrentlyUpdating(state, fields) {
            for (let fieldName in fields) {
                Vue.set(state.fieldsCurrentlyUpdating, fieldName, true)
            }
        },
        stopFieldsCurrentlyUpdating(state, fields) {
            for (let fieldName in fields) {
                Vue.set(state.fieldsCurrentlyUpdating, fieldName, false)
            }
        },
        setIsNameInEdition(state, isNameInEdition) {
            state.isNameInEdition = isNameInEdition
        },
        setLastFetchProjelPromise(state, lastFetchProjelPromise) {
            state.lastFetchProjelPromise = lastFetchProjelPromise
        },
        updateLabel(state, label) {
            if (!state.projel) {
                return
            }

            if (state.projel.type && state.projel.type.id == label.id) {
                state.projel.type = label
            }
            if (state.projel.priority && state.projel.priority.id == label.id) {
                state.projel.priority = label
            }
            if (state.projel.category && state.projel.category.id == label.id) {
                state.projel.category = label
            }
            if (state.projel.tags) {
                state.projel.tags = state.projel.tags.map((tag) =>
                    tag.id == label.id ? label : tag,
                )
            }
        },
        removeLabel(state, label) {
            if (!state.projel) {
                return
            }

            if (state.projel.type && state.projel.type.id == label.id) {
                state.projel.type = null
            }
            if (state.projel.priority && state.projel.priority.id == label.id) {
                state.projel.priority = null
            }
            if (state.projel.category && state.projel.category.id == label.id) {
                state.projel.category = null
            }
            if (state.projel.tags) {
                state.projel.tags = state.projel.tags.filter((tag) => tag.id != label.id)
            }
        },
    },
    getters: {
        isChannelRoute(state, getters, rootState) {
            return rootState.route.name.startsWith("channel")
        },
        isProjectRoute(state, getters, rootState) {
            return rootState.route.name.startsWith("project")
        },
        projelContentType(state, getters, rootState) {
            return getters.isChannelRoute
                ? rootState.contentTypes.Channel
                : rootState.contentTypes.Project
        },
        projelId(state, getters, rootState) {
            return parseInt(rootState.route.params.id)
        },
        inactiveMentionGroups(state) {
            if (_.isEmpty(state.projel)) return {}

            let channels = state.projel.channels || []
            let channelOwners = _.flatten(channels.map((channel) => channel.owners))
            return {
                owners: _.isEmpty(state.projel.owners),
                members: _.isEmpty(state.projel.members),
                channelOwners: _.isEmpty(channelOwners),
            }
        },
        sidebarHierarchyVisibilityKey(state, getters) {
            return `${getters.projelContentType.modelName}-${state.projel.id}`
        },
        isSidebarHierarchyVisible(state, getters) {
            return state.sidebarHierarchyVisibility[getters.sidebarHierarchyVisibilityKey]
        },
    },
    actions: {
        fetchProjel({ getters, commit }, { resetBeforeFetch }) {
            if (resetBeforeFetch) {
                commit("setProjel", {})
            }

            let url = getters.isChannelRoute ? urls.channels : urls.projects
            let fetchProjelPromise = $httpX({
                commit,
                name: "fetchProjel",
                method: "GET",
                url: url.format({ id: getters.projelId }),
                handle404: true,
            }).then((response) => {
                let projel = response.data
                commit("setProjel", projel)
                commit("projelDetail/linkedTasks/setLinkedTasks", projel.tasks, { root: true })
                commit("projelDetail/linkedAssets/setLinkedAssets", projel.assets, { root: true })
                // Populate the sharings store
                commit("sharings/setSharings", projel.sharings, { root: true })
            })

            commit("setLastFetchProjelPromise", fetchProjelPromise)
            return fetchProjelPromise
        },
        /**
         * Make a partial update for the given fields of the projel.
         * The data parameter are the new {field: value} to save.
         *
         * Ex :
         * partialUpdateProjel({
         *      name: "My Projel",
         *      tags: [4, 6]
         * })
         */
        partialUpdateProjel({ state, getters, commit, dispatch }, projelData) {
            commit("startFieldsCurrentlyUpdating", projelData)

            let url = getters.isChannelRoute ? urls.channels : urls.projects
            return $httpX({
                name: "partialUpdateProjel",
                commit,
                method: "PATCH",
                url: url.format({ id: state.projel.id }),
                data: projelData,
            })
                .then((response) => {
                    let projel = response.data
                    commit("setProjel", projel)
                    let event = getters.isChannelRoute
                        ? EVENTS.channelUpdated
                        : EVENTS.projectUpdated
                    dispatchEvent(event, projel)
                })
                .finally(() => {
                    commit("stopFieldsCurrentlyUpdating", projelData)
                })
        },

        closeProjel({ commit, getters, state }) {
            let url = getters.isChannelRoute ? urls.channelsClose : urls.projectsClose
            return $httpX({
                name: "closeProjel",
                commit,
                method: "PUT",
                url: url.format({ id: state.projel.id }),
            }).then((response) => {
                let projel = response.data
                commit("setProjel", projel)
                let event = getters.isChannelRoute ? EVENTS.channelClosed : EVENTS.projectClosed
                dispatchEvent(event, projel)
            })
        },

        softDeleteProjel({ commit, getters, state }) {
            let url = getters.isChannelRoute ? urls.channelsSoftDelete : urls.projectsSoftDelete
            return $httpX({
                name: "softDeleteProjel",
                commit,
                method: "PUT",
                url: url.format({ id: state.projel.id }),
            }).then((response) => {
                let event = getters.isChannelRoute ? EVENTS.channelDeleted : EVENTS.projectDeleted
                dispatchEvent(event, response.data)
            })
        },

        confirmProjelStateUpdate(
            { commit, getters, state },
            { projelStateUpdateRequested, notifyAuthor, comment },
        ) {
            let url = getters.isChannelRoute ? urls.channelsUpdateState : urls.projectsUpdateState
            return $httpX({
                name: "confirmProjelStateUpdate",
                method: "PUT",
                commit,
                url: url.format({ id: state.projel.id }),
                data: {
                    state: projelStateUpdateRequested,
                    notify_author: notifyAuthor,
                    comment: comment,
                },
            }).then((response) => {
                commit("setProjel", response.data)
            })
        },

        toggleSidebarHierarchyVisibility({ state, getters }) {
            Vue.set(
                state.sidebarHierarchyVisibility,
                getters.sidebarHierarchyVisibilityKey,
                !getters.isSidebarHierarchyVisible,
            )
            localSidebarHierarchyVisibility.set(state.sidebarHierarchyVisibility)
        },

        /***********************
         * Listeners to store events
         ************************/

        ...mapEvents({
            [EVENTS.labelUpdated]({ commit }, label) {
                commit("updateLabel", label)
            },

            [EVENTS.labelDeleted]({ commit }, label) {
                commit("removeLabel", label)
            },

            [EVENTS.itemCreated]({ state, commit }, item) {
                commit("setItemsCount", state.itemsCount + 1)
            },

            [EVENTS.itemTrashed]({ state, commit }, item) {
                commit("setItemsCount", state.itemsCount - 1)
            },

            [EVENTS.itemBulkTrashed]({ state, commit }, { itemIds }) {
                commit("setItemsCount", state.itemsCount - itemIds.length)
            },

            [EVENTS.itemBulkRemovedFromProjel]({ state, commit }, { itemIds }) {
                commit("setItemsCount", state.itemsCount - itemIds.length)
            },
        }),
    },
}
