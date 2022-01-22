import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

const UNREAD = "unread"
const READ = "read"

function createNotificationListData() {
    return {
        notifications: [],
        pagination: null,
    }
}

export default {
    namespaced: true,
    state: {
        unread: createNotificationListData(),
        read: createNotificationListData(),
    },
    mutations: {
        setNotifications(state, { notifications, listName }) {
            state[listName].notifications = notifications
        },
        appendToNotifications(state, { notifications, listName }) {
            state[listName].notifications = state[listName].notifications.concat(notifications)
        },
        insertNotification(state, { notification, listName }) {
            let notifications = state[listName].notifications
            let index = 0
            while (
                index < notifications.length &&
                notifications[index].send_at > notification.send_at
            ) {
                index++
            }
            notifications.splice(index, 0, notification)

            if (state[listName].pagination) {
                state[listName].pagination.count++
            }
        },
        removeNotification(state, { notification, listName }) {
            state[listName].notifications = state[listName].notifications.filter(
                (_notif) => _notif.id !== notification.id,
            )
            if (state[listName].pagination) {
                state[listName].pagination.count--
            }
        },
        setPagination(state, { pagination, listName }) {
            state[listName].pagination = pagination
        },
    },
    getters: {
        unreadCount(state) {
            return _.get(state, "unread.pagination.count", "?")
        },
        readCount(state) {
            return _.get(state, "read.pagination.count", "?")
        },
    },
    actions: {
        fetchNotifications({ state, commit }, { listName, append = false }) {
            let page, fetchName
            if (append) {
                page = state[listName].pagination.next
                fetchName = "appendNotifications"
            } else {
                page = 1
                fetchName = "fetchNotifications"
                commit("setPagination", { listName, pagination: null })
            }

            $httpX({
                name: fetchName,
                commit,
                url: urls.notificationsSubset.format({ listName }),
                params: { page },
            })
                .then((response) => {
                    commit("setPagination", {
                        listName,
                        pagination: _.omit(response.data, "objects"),
                    })
                    let notifications = response.data.objects
                    if (append) commit("appendToNotifications", { listName, notifications })
                    else commit("setNotifications", { listName, notifications })
                })
                .catch((errors) => {
                    commit("setPagination", { listName, pagination: null })
                })
        },
        toggleIsRead({ dispatch, commit }, notification) {
            let loadingName = "toggleIsRead" + notification.id
            $httpX({
                name: loadingName,
                commit,
                method: "PATCH",
                url: urls.notifications.format({ id: notification.id }),
                data: {
                    is_read: !notification.is_read,
                },
            }).then((response) => {
                notification.is_read = !notification.is_read

                let removeFrom, addTo, commitName
                if (notification.is_read) {
                    removeFrom = UNREAD
                    addTo = READ
                    commitName = "users/decrementUnreadNotificationCount"
                } else {
                    removeFrom = READ
                    addTo = UNREAD
                    commitName = "users/incrementUnreadNotificationCount"
                }
                // Give some time to the user to see its modification
                // Then remove the notification from the list
                setTimeout(() => {
                    commit("removeNotification", {
                        notification: notification,
                        listName: removeFrom,
                    })
                    commit("insertNotification", {
                        notification: notification,
                        listName: addTo,
                    })
                    commit("loading/resetLoading", loadingName, { root: true })
                }, 300)
                // Update the unread notification count badge on the Bell Icon in the User tools in MainMenu
                commit(commitName, {}, { root: true })
            })
        },
    },
}
