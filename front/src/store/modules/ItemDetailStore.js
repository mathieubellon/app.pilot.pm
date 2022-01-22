import _ from "lodash"
import Vue from "vue"
import urls from "@js/urls"
import { $httpX } from "@js/ajax.js"
import realtime from "@js/realtime"
import { getCurrentItemScroll, scrollItemTo } from "@js/items/itemsUtils"

import ActivityFeedStore from "@/store/modules/ActivityFeedStore.js"
import LinkedAssetsStore from "@/store/modules/LinkedAssetsStore.js"
import LinkedTasksStore from "@/store/modules/LinkedTasksStore.js"

import { ItemReadOnly } from "@js/items/ItemReadOnly"

import * as itemDecorationBoxes from "@js/items/itemDecorationBoxes"
import { EVENTS, mapEvents, dispatchEvent } from "@js/events"

let itemStoreInitialized = false
let sessionFetchPromise = null

const get_initial_state = () => ({
    /**
     * Ressources
     */
    // The main item resource we're viewing
    item: {},
    // An ItemReadOnly instance for the item content currently displayed (content + annotation + version)
    itemReadOnly: new ItemReadOnly({}),
    // List the history of the edit sessions of an item
    editSessions: [],
    // Read-only item when previewing a master translation
    masterTranslationPreview: new ItemReadOnly({}),

    /**
     * Panels
     */
    // Name of the right menu currently opened, or null if none is open
    openedDrawer: null,

    /**
     * Diff
     */
    // The version currently diffed with
    editSessionForDiff: null,
    // The version currently merged with
    editSessionForMergeTool: null,

    /**
     * UI Modes
     */
    // Keep track of fields that are currently being saved
    // {fieldName : true/false}
    fieldsCurrentlyUpdating: {},
    // Is the item editable ? (content and annotations)
    // An old version or a diff won't be editable.
    editable: true,
    // Should we display the merge tool
    isMergeToolActive: false,
    // A major version upgrade has been requested, the user need to confirm it
    createMajorVersionRequested: false,
    // Target version of the loading, when applicable : session or diff loading
    versionCurrentlyLoading: null,
    // We're currently exiting the diff mode
    exitingDiffMode: false,
})

export default {
    namespaced: true,
    modules: {
        activityFeed: ActivityFeedStore,
        linkedAssets: LinkedAssetsStore,
        linkedTasks: LinkedTasksStore,
    },
    state: get_initial_state(),
    mutations: {
        reset(state) {
            _.assign(state, get_initial_state())
        },

        /**
         * Ressources
         */
        setItem(state, item) {
            state.item = item
            if (item.id) {
                state.itemReadOnly = ItemReadOnly.fromItem(item)
            }
        },
        setItemFields(state, fields) {
            _.assign(state.item, fields)
            state.itemReadOnly = ItemReadOnly.fromItem(state.item)
        },
        setEditSessions(state, editSessions) {
            state.editSessions = editSessions
        },
        prependEditSession(state, editSession) {
            state.editSessions.unshift(editSession)
            // Keep the item version up to date ( new version )
            state.item.version = editSession.version
        },
        replaceFirstEditSession(state, editSession) {
            state.editSessions.splice(0, 1, editSession)
            // Keep the item version up to date ( major version upgrade )
            state.item.version = editSession.version
        },
        setEditSession(state, session) {
            state.itemReadOnly = ItemReadOnly.fromEditSession(session)
            state.editable = false
            state.editSessionForDiff = null
            state.createMajorVersionRequested = false
            state.versionCurrentlyLoading = null
        },
        showCurrentVersion(state) {
            if (state.item.id) {
                state.itemReadOnly = ItemReadOnly.fromItem(state.item)
            }
            state.editable = true
            state.isMergeToolActive = false
        },
        setMasterTranslationPreview(state, masterTranslation) {
            state.masterTranslationPreview = ItemReadOnly.fromItem(masterTranslation)
        },
        updateLabel(state, label) {
            if (state.item && state.item.tags) {
                state.item.tags = state.item.tags.map((tag) => (tag.id == label.id ? label : tag))
            }
        },
        removeLabel(state, label) {
            if (state.item && state.item.tags) {
                state.item.tags = state.item.tags.filter((tag) => tag.id != label.id)
            }
        },

        /**
         * Panels
         */
        setOpenedDrawer(state, openedDrawer) {
            state.openedDrawer = openedDrawer
            state.editable = openedDrawer != "history"

            state.isMergeToolActive = false
            state.createMajorVersionRequested = false
            state.editSessionForDiff = null
        },

        /**
         * Diff
         */
        setDiffEditSession(state, { editSessionForDiff, backendDiff }) {
            if (backendDiff) {
                state.itemReadOnly = ItemReadOnly.fromDiff(backendDiff)
            }
            state.editSessionForDiff = editSessionForDiff
            state.editable = false
            state.versionCurrentlyLoading = null
        },

        /**
         * UI Modes
         */
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
        openMergeTool(state, editSession) {
            state.isMergeToolActive = true
            state.editSessionForMergeTool = editSession
        },
        requestCreateMajorVersion(state) {
            state.createMajorVersionRequested = true
        },
        cancelCreateMajorVersion(state) {
            state.createMajorVersionRequested = false
        },
        setVersionCurrentlyLoading(state, version) {
            state.versionCurrentlyLoading = version
        },
        setExitingDiffMode(state, exitingDiffMode) {
            state.exitingDiffMode = exitingDiffMode
        },
    },
    getters: {
        itemId(state, getters, rootState) {
            return parseInt(rootState.route.params.id)
        },

        /**
         * UI Modes
         */
        isHistoryPanelOpen(state) {
            return state.openedDrawer == "history"
        },
        isDiffModeActive(state) {
            return state.itemReadOnly.isDiff
        },
        lastEditSession(state) {
            return state.editSessions[0]
        },

        /**
         * Tells if a version is the current (latest) one.
         * If called with a parameter, tells if the parameter is the current version.
         * If called without parameter, tells if the currently displayed version is the current version.
         *
         * @param version A version string : "1.5"
         * @returns {boolean} true if this is the current version
         */
        isCurrentVersion: (state) => (version) => {
            return version == state.item.version
        },

        /**
         * Given an EditSession, returns the minor version number
         * Example : "2.6" ==> 6
         */
        getMinorVersion: (state) => (editSession) => {
            if (!editSession) {
                return null
            }
            return parseInt(editSession.version.split(".")[1])
        },

        /**
         * Given a version string, find the corresponding EditSession
         *
         * @param version A version string : "1.5"
         * @returns {*} An EditSession instance if found, else undefined
         */
        findEditSession: (state) => (version) => {
            return _.find(state.editSessions, (session) => session.version == version)
        },

        /**
         * Given a version string, find the EditSession corresponding
         * to the previous version
         *
         * @param version A version string : "1.5"
         * @returns {*} An EditSession instance if found, else undefined
         */
        getPreviousEditSession: (state) => (version) => {
            let lastIndex = state.editSessions.length - 1
            let versionIndex = _.indexOf(_.map(state.editSessions, "version"), version)
            if (versionIndex == -1) {
                versionIndex = lastIndex
            }
            return state.editSessions[Math.min(lastIndex, versionIndex + 1)]
        },

        /**
         * Tells if a editSession can be restored.
         * The current version cannot be restored
         *
         * @param editSession An EditSession instance
         * @returns {boolean} true if this is snapshot can be restored
         */
        canRestore: (state, getters) => (editSession) => {
            return !getters.isCurrentVersion(editSession.version)
        },

        isItemLinked: (state) => (itemId) => {
            return _.some(state.item.translations, (item) => item.id == itemId)
        },
        inactiveMentionGroups(state) {
            return {
                owners: _.isEmpty(state.item.owners),
                channelOwners:
                    !state.item.channels ||
                    !_.some(state.item.channels.map((channel) => channel.has_owners)),
            }
        },
    },
    actions: {
        /***********************
         * Item Fetch / save
         ************************/

        initItemStore({ state, commit, dispatch }) {
            if (itemStoreInitialized) {
                return
            }

            realtime.addMessageHandler(realtime.S2C_MESSAGES.BROADCAST_ITEM, (message) => {
                // The item broadcasting does not customize those two fields for each users.
                // We need to copy them over.
                let item = message.item
                item.user_has_access = state.item.user_has_access
                item.user_has_private_perm = state.item.user_has_private_perm
                dispatch("receiveItem", item)
                dispatch("receiveLatestSession", message.session)
            })
            realtime.addMessageHandler(realtime.S2C_MESSAGES.BROADCAST_ITEM_CHANGES, (message) => {
                dispatch("receiveLatestSession", message.session)

                let updates = {
                    content: _.clone(state.item.content),
                }
                for (let fieldName in message.changes || {}) {
                    let change = message.changes[fieldName]
                    if ("value" in change) {
                        updates.content[fieldName] = change.value
                    }
                }
                // When the title change in the content, we must update the field item.title
                updates.title = _.get(message, "changes.title.value", state.item.title)
                commit("setItemFields", updates)
                dispatchEvent(EVENTS.itemUpdated, state.item)
            })

            itemStoreInitialized = true
        },

        receiveItem({ commit, dispatch }, item) {
            commit("setItem", item)
            commit("itemContentForm/setItem", item, { root: true })
            // Populate the linkedTasks store
            commit("itemDetail/linkedTasks/setLinkedTasks", item.tasks, { root: true })
            // Populate the linkedAssets store
            commit("itemDetail/linkedAssets/setLinkedAssets", item.assets, { root: true })
            // Populate the sharings store
            commit("sharings/setSharings", item.sharings, { root: true })

            dispatchEvent(EVENTS.itemUpdated, item)
        },

        fetchItem({ getters, commit, dispatch }) {
            commit("reset")
            commit("itemContentForm/reset", null, { root: true })
            dispatch("initItemStore")
            commit("activityFeed/setActivities", [])

            return new Promise((resolve, reject) => {
                $httpX({
                    name: "fetchItem",
                    commit,
                    url: urls.items.format({ id: getters.itemId }),
                    handle404: true,
                })
                    .then((response) => {
                        dispatch("receiveItem", response.data)
                        resolve()
                    })
                    .catch((error) => {
                        reject()
                    })
            })
        },

        /**
         * Make a partial update for the given fields of the item.
         * The data parameter are the new {field: value} to save.
         *
         * Ex :
         * partialUpdateItem({
         *      guidelines: "Awesome",
         *      photographer_needed: true
         * })
         */
        partialUpdateItem({ dispatch, state, commit }, itemData) {
            commit("startFieldsCurrentlyUpdating", itemData)
            return $httpX({
                name: "partialUpdateItem",
                commit,
                method: "PATCH",
                url: urls.items.format({ id: state.item.id }),
                data: itemData,
            })
                .then((response) => {
                    dispatch("receiveItem", response.data)
                })
                .finally(() => {
                    commit("stopFieldsCurrentlyUpdating", itemData)
                })
        },

        /**
         * Link/Unlink other items
         */
        linkItem({ state, getters, commit, dispatch }, linkedItem) {
            if (getters.isItemLinked(linkedItem.id)) return

            return dispatch("partialUpdateItem", {
                translations_id: state.item.translations_id.concat([linkedItem.id]),
            })
        },

        unlinkItem({ state, getters, commit, dispatch }, linkedItem) {
            if (!getters.isItemLinked(linkedItem.id)) return

            dispatch("partialUpdateItem", {
                translations_id: _.without(state.item.translations_id, linkedItem.id),
            })
        },

        /**
         * Toggle the item.frozen flag
         */
        toggleFrozen({ state, commit, dispatch }, frozen_message) {
            dispatch("partialUpdateItem", {
                frozen: !state.item.frozen,
                frozen_message,
            })
        },

        /**
         * Toggle the item.is_private flag
         */
        toggleIsPrivate({ state, commit, dispatch }) {
            dispatch("partialUpdateItem", {
                is_private: !state.item.is_private,
            })
        },

        putInTrash({ commit, state, dispatch }) {
            $httpX({
                name: "putInTrash",
                commit,
                method: "PUT",
                url: urls.itemPutInTrash.format({ id: state.item.id }),
            }).then((response) => {
                commit("setItem", response.data)

                dispatchEvent(EVENTS.itemTrashed, response.data)
            })
        },
        restoreFromTrash({ commit, state, dispatch }) {
            $httpX({
                name: "itemRestoreFromTrash",
                commit,
                method: "PUT",
                url: urls.itemRestoreFromTrash.format({ id: state.item.id }),
            }).then((response) => {
                dispatch("receiveItem", response.data)
            })
        },

        /***********************
         * Panels
         ************************/

        /**
         * Open one right panel by name.
         * Populate the panel content if needed, and align the decoration boxes.
         *
         * @param drawerName
         */
        openDrawer({ state, getters, commit, dispatch }, drawerName) {
            if (!state.item.id) {
                return
            }
            commit("setOpenedDrawer", drawerName)
            if (getters.isHistoryPanelOpen) {
                sessionFetchPromise.then(() => {
                    dispatch("showEditSession", {
                        editSession: state.editSessions[0],
                        withDiff: false,
                    })
                })
            }
        },

        /**
         * Close the currently opened right panel.
         * Align the decoration boxes
         */
        closePanel({ state, commit, dispatch }) {
            commit("showCurrentVersion")
            commit("setOpenedDrawer", null)
        },

        /***********************
         * History ( Sessions, Diff )
         ************************/

        /**
         * Receive the session state from the realtime server
         */
        receiveLatestSession({ state, getters, commit, rootState }, latestSession) {
            if (!latestSession || !state.editSessions[0]) {
                return
            }
            if (state.editSessions[0].id == latestSession.id) {
                commit("replaceFirstEditSession", latestSession)
            } else {
                commit("prependEditSession", latestSession)
            }
        },

        /**
         * Fetch all edit sessions ( light serialization without the content )
         */
        fetchEditSessions({ getters, commit }) {
            sessionFetchPromise = $httpX({
                name: "fetchEditSessions",
                commit,
                url: urls.itemsSession.format({
                    itemId: getters.itemId,
                }),
            }).then((response) => {
                commit("setEditSessions", response.data)
            })
            return sessionFetchPromise
        },

        /**
         * Fetch an EditSession, then set it into the state
         */
        fetchEditSession({ state, commit }, editSession) {
            commit("setVersionCurrentlyLoading", editSession.version)
            return $httpX({
                name: "fetchEditSession",
                commit,
                url: urls.itemsSession.format({
                    itemId: state.item.id,
                    id: editSession.id,
                }),
            }).then((response) => {
                commit("setEditSession", response.data)
            })
        },

        /**
         * Fetch a diff between two versions, then display it
         */
        fetchItemDiff(
            { state, getters, commit, dispatch },
            { editSessionForDiff, baseEditSession },
        ) {
            commit("setVersionCurrentlyLoading", baseEditSession.version)

            return $httpX({
                name: "fetchItemDiff",
                commit,
                url: urls.itemDiff.format({
                    id: state.item.id,
                    leftSessionId: editSessionForDiff.id,
                    rightSessionId: baseEditSession.id,
                }),
            }).then((response) => {
                commit("setDiffEditSession", {
                    editSessionForDiff: editSessionForDiff,
                    backendDiff: response.data,
                })
            })
        },

        /**
         * Display an EditSession, taking into account the current diffing mode.
         * Keep the scrolling context of the Item.
         */
        showEditSession(
            { state, getters, commit, dispatch },
            { editSession, withDiff, editSessionForDiff },
        ) {
            // Remember the scroll position, to keep the user into his current context
            let oldScrollTop = getCurrentItemScroll()
            let promise

            if (withDiff) {
                if (!editSession) {
                    editSession = getters.findEditSession(state.itemReadOnly.version)
                }
                if (!editSessionForDiff) {
                    editSessionForDiff = getters.getPreviousEditSession(editSession.version)
                }

                promise = dispatch("fetchItemDiff", {
                    editSessionForDiff,
                    baseEditSession: editSession,
                })
            } else {
                promise = dispatch("fetchEditSession", editSession)
            }

            // Restore the scroll position
            promise.then(() => scrollItemTo({ topCoord: oldScrollTop }))
            return promise
        },

        exitDiffMode({ state, getters, commit, dispatch }) {
            commit("setExitingDiffMode", true)
            commit("setDiffEditSession", { editSessionForDiff: null })
            let editSession = getters.findEditSession(state.itemReadOnly.version)
            dispatch("showEditSession", { editSession, withDiff: false }).then(() =>
                commit("setExitingDiffMode", false),
            )
        },

        showMergeToolWithSnapshot({ state, getters, commit, dispatch }, editSession) {
            // let previousVersion = getters.getPreviousEditSession(editSession.version)
            $httpX({
                name: "showMergeToolWithSnapshot",
                commit,
                url: urls.itemsSession.format({
                    itemId: state.item.id,
                    id: editSession.id,
                }),
            }).then((response) => {
                commit("setOpenedDrawer", null)
                commit("openMergeTool", response.data)
            })
        },

        /**
         * Create a new EditSession with a major version.
         *
         * The new major version will be identical to the current version.
         * Can only be done if the previous version is not already a major version ( X.0 )
         */
        createMajorVersion({ state, commit }) {
            $httpX({
                name: "createMajorVersion",
                commit,
                method: "PUT",
                url: urls.itemCreateMajorVersion.format({
                    id: state.item.id,
                }),
            }).then((response) => {
                // Update the upgraded editSession
                let editSession = response.data
                commit("prependEditSession", editSession)
                commit("setEditSession", editSession)
            })
        },

        /***********************
         * Restoration
         ************************/

        /**
         * Create a new version of the item by restoring an old version.
         */
        restore({ state, getters, commit, dispatch }, editSession) {
            if (!getters.canRestore(editSession)) {
                return
            }

            $httpX({
                name: "itemRestore",
                commit,
                url: urls.itemRestoreSession.format({ id: state.item.id }),
                method: "PUT",
                data: {
                    session_id: editSession.id,
                },
            }).then((response) => {
                dispatch("closePanel")
            })
        },

        /***********************
         * Translations
         ************************/

        fetchMasterTranslationPreview({ state, commit }) {
            $httpX({
                name: `fetchMasterTranslationPreview`,
                commit,
                method: "GET",
                url: urls.items.format({ id: state.item.master_translation.id }),
            }).then((response) => {
                commit("setMasterTranslationPreview", response.data)
            })
        },

        /***********************
         * Alignment for decoration boxes
         ************************/
        alignDecorationBoxes({ state, rootState, rootGetters }) {
            let pmFieldsNames = rootGetters["itemContentForm/pmFieldsNames"]
            let editors = state.editable
                ? rootState.itemContentForm.tiptapEditors
                : rootState.itemContentForm.readOnlyTiptapEditors

            for (let pmFieldName of pmFieldsNames) {
                let editor = editors[pmFieldName]
                if (!editor) {
                    return
                }
                itemDecorationBoxes.alignBoxes(editor.view)
            }
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
        }),
    },
}
