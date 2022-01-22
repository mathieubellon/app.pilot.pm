import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { EVENTS, mapEvents } from "@js/events"

let popIndex = 0

function isTaskTodoByUser(user, task) {
    return !task.done && task.assignees_id.indexOf(user.id) != -1
}

export default {
    namespaced: true,
    state: {
        // The user currently connected
        me: {},

        // The messages we show to the user.
        // May be from the backend messaging infrastructure,
        // or a poppedMessage from the frontend.
        messages: [],

        // When the current user click on the username of another user,
        // it will examine its profile on an offpanel.
        // Store this examined user here
        userExamined: {},
    },
    mutations: {
        setUserMe(state, me) {
            state.me = me
            if (me.unread_messages) {
                state.messages = [...me.unread_messages]
            }
        },
        setUserMeField(state, { fieldPath, value }) {
            _.set(state.me, fieldPath, value)
        },
        setUnreadNotificationCount(state, unreadNotificationCount) {
            state.me.unread_notifications_count = unreadNotificationCount
        },
        incrementUnreadNotificationCount(state) {
            state.me.unread_notifications_count++
        },
        decrementUnreadNotificationCount(state) {
            state.me.unread_notifications_count--
        },
        incrementUndoneTasksCount(state) {
            state.me.undone_tasks_count++
        },
        decrementUndoneTasksCount(state) {
            state.me.undone_tasks_count--
        },
        setUserExamined(state, userExamined) {
            state.userExamined = userExamined
        },
        removeMessage(state, message) {
            state.messages = state.messages.filter((m) => m != message)
        },
        popMessage(state, poppedMessage) {
            // If the message already exists, make it blink, and do not add it anew.
            for (let message of state.messages) {
                if (message.content.fr == poppedMessage) {
                    message.twinkle = true
                    setTimeout(() => (message.twinkle = false), 4000)
                    return
                }
            }

            // The message is not already present, we can add it
            state.messages = [
                ...state.messages,
                {
                    id: "pop" + popIndex++,
                    type: "pop",
                    content: {
                        fr: poppedMessage,
                        en: poppedMessage,
                    },
                    twinkle: false,
                },
            ]
        },
    },
    getters: {
        /**
         * Always return a permission object.
         * When users.me or users.me.permissions is undefined,
         * will default to an object with no permission allowed
         */
        myPermissions: (state) => {
            return _.get(state, "me.permissions", {
                is_organization_admin: false,
                is_admin: false,
                is_editor: false,
                is_restricted_editor: false,
            })
        },
    },
    actions: {
        saveUserMe({ state, commit }) {
            if (window.pilot.user.isAnonymous) {
                return
            }
            $httpX({
                name: "saveUserMe",
                commit,
                method: "PUT",
                url: urls.usersMe,
                data: state.me,
            }).then((response) => {
                commit("setUserMe", response.data)
            })
        },
        partialUpdateUser({ state, commit, dispatch }, userData) {
            if (window.pilot.user.isAnonymous) {
                return
            }
            $httpX({
                name: "partialUpdateUser",
                commit,
                method: "PATCH",
                url: urls.usersMe,
                data: userData,
            }).then((response) => {
                commit("setUserMe", response.data)
            })
        },
        updateUserField({ state, commit, dispatch }, { fieldPath, value }) {
            commit("setUserMeField", { fieldPath, value })
            dispatch("saveUserMe")
        },
        fetchUserExamined({ state, commit }, userId) {
            $httpX({
                name: "fetchUserExamined",
                commit,
                method: "GET",
                url: urls.users.format({ id: userId }),
            }).then((response) => {
                commit("setUserExamined", response.data)
            })
        },
        setMessageAsRead({ dispatch, commit }, message) {
            $httpX({
                name: "`setMessageAsRead-${message.id}`",
                commit,
                method: "POST",
                url: urls.usersMeSetMessageAsRead,
                data: {
                    message_id: message.id,
                },
            })
        },

        /***********************
         * Listeners to store events
         ************************/

        ...mapEvents({
            [EVENTS.taskCreated]({ state, commit }, { task }) {
                if (isTaskTodoByUser(state.me, task)) {
                    commit("incrementUndoneTasksCount")
                }
            },

            [EVENTS.taskUpdated]({ state, commit }, { task, taskBefore }) {
                let assignedToMe = isTaskTodoByUser(state.me, task)
                let assignedToMeBefore = isTaskTodoByUser(state.me, taskBefore)
                if (assignedToMe && !assignedToMeBefore) {
                    commit("incrementUndoneTasksCount")
                }
                if (!assignedToMe && assignedToMeBefore) {
                    commit("decrementUndoneTasksCount")
                }
            },

            [EVENTS.taskDeleted]({ state, commit, dispatch }, { task }) {
                if (isTaskTodoByUser(state.me, task)) {
                    commit("decrementUndoneTasksCount")
                }
            },
        }),
    },
}
