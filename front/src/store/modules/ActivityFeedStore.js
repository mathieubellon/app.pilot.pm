import _ from "lodash"

import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

export default {
    namespaced: true,
    state: () => ({
        activities: [],
        contentType: null,
        objectId: null,
        queryParams: {},
        pagination: null,
    }),
    mutations: {
        initActivityFeedStore(state, { contentType = null, objectId = null, queryParams = {} }) {
            state.contentType = contentType
            state.objectId = objectId
            state.queryParams = queryParams
        },
        setActivities(state, activities) {
            state.activities = activities
        },
        prependActivity(state, activity) {
            state.activities.unshift(activity)
        },
        appendToActivities(state, activities) {
            state.activities = state.activities.concat(activities)
        },
        updateActivity(state, activity) {
            state.activities = state.activities.map((oldActivity) =>
                oldActivity.id == activity.id ? activity : oldActivity,
            )
        },
        setPagination(state, pagination) {
            state.pagination = pagination
        },
    },
    getters: {
        isActivityListEmpty(state) {
            return state.activities.length === 0
        },
        commentsCount(state) {
            return state.activities.filter((a) => a.is_comment).length
        },
    },
    actions: {
        fetchActivities({ state, commit }, append = false) {
            let params = _.clone(state.queryParams)
            if (state.contentType) params.content_type_id = state.contentType.id
            if (state.objectId) params.object_id = state.objectId
            // We only paginate for the global activity stream (dashboard),
            // where all activities are mixed.
            // A single instance activity stream is not paginated.
            params.paginated = !Boolean(state.objectId)

            if (params.paginated) {
                params.page = append ? state.pagination.next : 1
            }

            let fetchName = append ? "appendActivities" : "fetchActivities"

            return $httpX({
                name: fetchName,
                commit,
                url: urls.activity,
                params: params,
            })
                .then((response) => {
                    let activities
                    if (params.paginated) {
                        commit("setPagination", _.omit(response.data, "objects"))
                        activities = response.data.objects
                    } else {
                        commit("setPagination", null)
                        activities = response.data
                    }

                    if (append) {
                        commit("appendToActivities", activities)
                    } else {
                        commit("setActivities", activities)
                    }
                })
                .catch((errors) => {
                    commit("setPagination", null)
                })
        },
        createComment({ state, getters, commit }, commentContent) {
            return $httpX({
                name: "createComment",
                commit,
                url: urls.commentsCreate,
                method: "POST",
                data: {
                    comment_content: commentContent,
                    content_type_id: state.contentType.id,
                    object_id: state.objectId,
                },
            }).then((response) => {
                commit("prependActivity", response.data)
            })
        },
        editComment({ state, getters, commit }, { activityId, commentContent }) {
            return $httpX({
                name: "editComment",
                commit,
                url: urls.commentsEdit,
                method: "POST",
                data: {
                    activity_id: activityId,
                    comment_content: commentContent,
                },
            }).then((response) => {
                commit("updateActivity", response.data)
            })
        },
        deleteComment({ state, getters, commit }, { activityId }) {
            return $httpX({
                name: "deleteComment",
                commit,
                url: urls.commentsDelete,
                method: "POST",
                data: {
                    activity_id: activityId,
                },
            }).then((response) => {
                commit("updateActivity", response.data)
            })
        },
    },
}
