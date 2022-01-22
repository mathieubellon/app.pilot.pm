import _ from "lodash"
import Vue from "vue"
import moment from "moment"
import { sortByAlphaString } from "@js/utils"
import { $http } from "@js/ajax.js"
import realtime from "@js/realtime"
import urls from "@js/urls"
import i18n from "@js/i18n"
import $monitoring from "@js/monitoring"

import { getAllFieldSchemas, createItemValidation, createItemWarnings } from "@js/items/itemsUtils"
import { getRandomId } from "@js/utils.js"
import { SAVING_RECOVERY_STATE, ItemSavingState } from "@js/items/itemSavingState"

// In miliseconds
const SAVING_LOADER_MIN_DURATION = 500
const SAVING_THROTTLE_TIME = 300
const SAVING_VERIFICATION_DELAY = 1000 * 6 // 6 seconds

export const REALTIME_STATES = {
    connecting: "connecting",
    connected: "connected",
    saving: "saving",
    conflict: "conflict",
    desynchronized: "desynchronized",
}

function getAllItemFieldSchemas(state) {
    let content = _.get(state, "itemEditable.content")
    if (!state.contentSchema || !content) {
        return []
    }
    return getAllFieldSchemas(state.contentSchema, content)
}

function getItemFieldSchema(state, fieldName) {
    return _.find(getAllItemFieldSchemas(state), (schema) => schema.name == fieldName)
}

function setValidation(state) {
    // If there was already a validation object, we must destroy it to prevent memory leaks
    if (state.validation) {
        state.validation.freeMemory()
    }
    // Generate a new vuelidate object
    state.validation = createItemValidation(
        state.contentSchema,
        // We don't validate metadata yet on the item detail page.
        // Comment it to prevent validation errors
        //state.item.metadata_schema,
        {},
        state.itemEditable,
    )

    // If there was already a warnings object, we must destroy it to prevent memory leaks
    if (state.warnings) {
        state.warnings.freeMemory()
    }
    // Generate a new vuelidate object
    state.warnings = createItemWarnings(state.contentSchema, state.itemEditable)
}

const get_initial_state = () => ({
    itemId: null,
    // The content schema
    contentSchema: [],
    // The editable content, with its annotations
    itemEditable: {
        content: {},
        annotations: {},
    },
    // The annotations that go with the itemEditable
    // Vuelidate validation object
    validation: null,
    warnings: null,

    lastEditor: null,
    lastEditionDatetime: null,

    /**
     * Prosemirror-specific
     */
    // fieldName --> tiptap editor object
    tiptapEditors: {},
    // fieldName --> tiptap editor object
    readOnlyTiptapEditors: {},
    // fieldName --> annotationManager
    annotationManagers: {},
    // fieldName --> annotationManager
    readOnlyAnnotationManagers: {},

    /**
     * Realtime
     */
    myRealtimeUser: {},
    myRealtimeClientId: null,
    realtimeUsers: [],
    // The server will disconnect this client after too much inactivity.
    // In this case, we'll display a message to the user.
    isDisconnectedAfterInactivity: false,
    // Track saving start time and recovery attempt
    savingState: null,
    // Selection that is not sent yet, between changes confirmation
    pendingSelection: null,
    // Changes that are not been sent yet, between changes confirmation
    // fieldName -> pendingChanges
    pendingChanges: {},
    // Changes that have been sent, but are not confirmed yet
    // fieldName -> unconfirmedChange
    unconfirmedChanges: {},
    // Confirmed versions for each fields
    // fieldName -> version number
    fieldVersions: {},
    // The non-prosemirror fields in conflict with another user
    // fieldName -> {value, clientId, version}
    conflictedFields: {},
    // Flag used when realtime is disconnected and an xhr save
    // could not be made because the content is not up to date
    desynchronized: false,
    // Datetime of the oldest unconfirmed change
    unconfirmedChangeMoment: null,
    // Datetime of the last confirmed save by the server, for a local change
    lastSuccessfulSaveMoment: moment(),
    // When a remote user made a version restoration
    remoteVersionRestoration: null,
})

export default {
    namespaced: true,
    state: get_initial_state,
    mutations: {
        reset(state) {
            if (state.validation) {
                state.validation.freeMemory()
            }
            if (state.warnings) {
                state.warnings.freeMemory()
            }
            _.assign(state, get_initial_state())
        },

        setItem(state, item) {
            state.itemId = item.id
            state.fieldVersions = item.field_versions

            // Make a deep copy for the content where we'll make the edition.
            // and make a deep copy so we don't impact the original item
            state.itemEditable = {
                content: _.cloneDeep(item.content),
                annotations: _.cloneDeep(item.annotations) || {},
            }
            state.contentSchema = item.item_type.content_schema

            setValidation(state)

            state.lastEditor = item.last_editor
            state.lastEditionDatetime = item.last_edition_datetime
        },

        setItemContentField(state, { fieldName, value }) {
            if (value === undefined) {
                return
            }

            let isNewField = state.itemEditable.content.hasOwnProperty(fieldName)

            Vue.set(state.itemEditable.content, fieldName, value)

            // Re-create the validation to take into account the new elastic values
            if (isNewField) {
                setValidation(state)
            }
        },

        setFieldAnnotations(state, { annotationsKey, annotations }) {
            if (state.itemEditable.annotations) {
                Vue.set(state.itemEditable.annotations, annotationsKey, annotations)
            }
        },

        setLastEditor(state, lastEditor) {
            state.lastEditor = lastEditor
        },

        setLastEditionDatetime(state, lastEditionDatetime) {
            state.lastEditionDatetime = lastEditionDatetime
        },

        /**
         * Realtime
         */
        setMyRealtimeUser(state, myRealtimeUser) {
            // Don't generate another clientId with randomId if the users are the same
            if (_.isEqual(state.myRealtimeUser, myRealtimeUser)) {
                return
            }

            state.myRealtimeUser = myRealtimeUser
            // We add a random id to distinguish between multiple tabs/windows
            // opened by the same user on the same content.
            // We use '§' as a separator character because it's not allowed into email address,
            // so we're sure it won't be used in myRealtimeUser.id by external users on item sharings
            state.myRealtimeClientId = myRealtimeUser.id + "§" + getRandomId()
        },

        throttledSetRealtimeUsers: _.throttle(
            (state, realtimeUsers) => {
                state.realtimeUsers = sortByAlphaString(realtimeUsers, (user) => user.username)
            },
            1000,
            { leading: true, trailing: true },
        ),

        setSavingState(state, savingState) {
            state.savingState = savingState
        },

        addPendingChange(
            state,
            { fieldName, value, annotations, annotationsKey, steps, selection, action },
        ) {
            let changes = _.cloneDeep(state.pendingChanges)
            let unconfirmedChange = state.unconfirmedChanges[fieldName] || {}

            // change.version will be set into sendPendingChanges
            let change = {
                clientId: state.myRealtimeClientId,
                value,
            }

            if (action) {
                change.action = action
            }

            if (steps) {
                // Remove the steps that we already sent to the central authority
                if (unconfirmedChange && unconfirmedChange.steps) {
                    steps = steps.slice(unconfirmedChange.steps.length)
                }
                change.steps = steps
            }
            if (annotations) {
                if (!annotationsKey) {
                    annotationsKey = fieldName
                }

                // Make a clean copy of the annotations
                annotations = _.cloneDeep(annotations)
                // Remove pixel geometry from image annotations, we don't need to store them
                _.forEach(annotations, (annotation) => {
                    if (annotation.shape) {
                        delete annotation.shape.pixelGeometry
                    }
                })

                change.annotationsKey = annotationsKey
                change.annotations = annotations
            }
            changes[fieldName] = change
            state.pendingChanges = changes
            state.pendingSelection = selection
        },

        preparePendingChangesForSending(state) {
            // We're about to send the pending changes, we can now set their version
            for (let fieldName in state.pendingChanges) {
                let change = state.pendingChanges[fieldName]
                // We set the version only when sending, so we're perfectly accurate.
                // If we set it in "addPendingChange", the version may increase
                // before we have the chance to actually send the change.
                change.version = state.fieldVersions[fieldName] || 0
                state.unconfirmedChanges[fieldName] = change
            }

            if (!state.unconfirmedChangeMoment) {
                state.unconfirmedChangeMoment = moment()
            }
        },

        pendingChangesHaveBeenSent(state) {
            // The pending changes have been sent and are now unconfirmed,
            // we must clear the pendingChanges storage.
            state.pendingChanges = {}
            state.pendingSelection = null
        },

        confirmVersion(state, { fieldName, version, isRemoteChange }) {
            // Bump the synchronized versions number
            Vue.set(state.fieldVersions, fieldName, version)
            // When the version confirmation has been triggered by a remote change,
            // discard the corresponding pending change, it's now unsynchronized.
            // If it's a prosemirror field, the Collab module will rebase to re-synchronize,
            // and generate a new pendingChange with the rebased steps.
            // If it's a normal field, a conflict has been stored ( with setConflictedField ) and will be displayed.
            if (isRemoteChange) {
                Vue.delete(state.pendingChanges, fieldName)
            }
            // Unconfirmed changes with a version below the received version are now confirmed
            let change = state.unconfirmedChanges[fieldName]
            if (change && change.version < version) {
                Vue.delete(state.unconfirmedChanges, fieldName)
            }

            if (!isRemoteChange) {
                state.unconfirmedChangeMoment = null
                state.lastSuccessfulSaveMoment = moment()
            }
        },

        setConflictedField(state, { fieldName, value, editor }) {
            Vue.set(state.conflictedFields, fieldName, { value, editor })
        },

        resolveConflictedField(state, fieldName) {
            Vue.delete(state.conflictedFields, fieldName)
        },

        setDesynchronized(state, desynchronized) {
            state.desynchronized = desynchronized
        },

        setRemoteVersionRestoration(state, remoteVersionRestoration) {
            state.remoteVersionRestoration = remoteVersionRestoration
        },

        /**
         * Prosemirror-specific
         */
        registerTiptapEditor(state, { fieldName, editor, readOnly }) {
            if (readOnly) state.readOnlyTiptapEditors[fieldName] = editor
            else state.tiptapEditors[fieldName] = editor
        },

        registerAnnotationManager(state, { key, annotationManager, readOnly }) {
            if (readOnly) Vue.set(state.readOnlyAnnotationManagers, key, annotationManager)
            else Vue.set(state.annotationManagers, key, annotationManager)
        },
    },
    getters: {
        allFieldSchemas(state) {
            return getAllItemFieldSchemas(state)
        },

        fieldsNames(state, getters) {
            return getters.allFieldSchemas.map((schema) => schema.name)
        },

        pmFieldsNames(state, getters) {
            return getters.allFieldSchemas
                .filter((schema) => schema.is_prosemirror)
                .map((schema) => schema.name)
        },

        /**
         * Realtime
         */
        // Return a mapping fieldName -> activityType -> [users]
        realtimeUserActivites(state, getters) {
            let activities = {}
            for (let fieldName of getters.fieldsNames) {
                activities[fieldName] = {
                    focus: [],
                    updating: [],
                }
            }
            for (let user of state.realtimeUsers) {
                if (user.field_updating && activities[user.field_updating])
                    activities[user.field_updating].updating.push(user)
                else if (user.field_focus && activities[user.field_focus])
                    activities[user.field_focus].focus.push(user)
            }
            return activities
        },

        anyPendingChanges: (state) => {
            return Object.keys(state.pendingChanges).length > 0
        },

        anyUnconfirmedChanges: (state) => {
            return Object.keys(state.unconfirmedChanges).length > 0
        },

        anyConflictedFields: (state) => {
            return Object.keys(state.conflictedFields).length > 0
        },

        // The user-understandable state of the real time saving
        currentRealtimeState: (state, getters) => {
            if (
                realtime.state == realtime.STATES.CONNECTING ||
                realtime.state == realtime.STATES.INITIAL
            ) {
                return REALTIME_STATES.connecting
            } else if (state.desynchronized || state.isDisconnectedAfterInactivity) {
                return REALTIME_STATES.desynchronized
            } else if (state.savingState && !state.savingState.isResolved) {
                return REALTIME_STATES.saving
            } else if (getters.anyConflictedFields) {
                return REALTIME_STATES.conflict
            } else if (
                realtime.state == realtime.STATES.OPEN ||
                realtime.state == realtime.STATES.CLOSED
            ) {
                return REALTIME_STATES.connected
            } else {
                console.error(`Unexpected realtime state : ${this.realtime.state}`)
                return REALTIME_STATES.desynchronized
            }
        },

        /**
         * Prosemirror-specific
         */
        areAnnotationManagersReady(state) {
            for (let fieldName in state.annotationManagers) {
                let annotationManager = state.annotationManagers[fieldName]
                // If any image annotator is not ready, then the annotation manager is not ready
                if (annotationManager.type == "image" && !annotationManager.annotator.ready) {
                    return false
                }
            }
            return true
        },
    },
    actions: {
        initRealtime({ state, commit, dispatch }, { itemId, realtimeUser }) {
            commit("setMyRealtimeUser", realtimeUser)

            realtime.addMessageHandler(realtime.S2C_MESSAGES.BROADCAST_USERS_ON_ITEM, (message) => {
                dispatch("receiveRealtimeUsers", message.users)
            })
            realtime.addMessageHandler(realtime.S2C_MESSAGES.BROADCAST_ITEM, (message) => {
                let { item, restored_version, restored_by } = message
                if (restored_version && restored_by.id != realtimeUser.id) {
                    commit("setRemoteVersionRestoration", { restored_version, restored_by })
                    commit("offPanel/openOffPanel", "remoteVersionRestoration", { root: true })
                }
                commit("setItem", item)
            })
            realtime.addMessageHandler(realtime.S2C_MESSAGES.BROADCAST_ITEM_CHANGES, (message) => {
                dispatch("receiveItemContentChanges", message)
            })
            realtime.addMessageHandler(realtime.S2C_MESSAGES.INVALID_CHANGES, (message) => {
                dispatch("endSaving")
                // right now the only INVALID_CHANGES message we can get is concerning the base64 images
                dispatch("alertBase64Image")
                commit("setDesynchronized", true)
            })
            realtime.connect()
            realtime.connectPromise.then(() => {
                realtime.registerOnItem(itemId)
            })
        },

        /**
         * Called when a saving has ended, either successfully or with invalid changes.
         * Will stop the saving loader.
         * Will clean the recovery state.
         */
        endSaving({ state, commit, rootState }) {
            // state may be null because endSaving may be called in a setTimeout after we left the current page
            state = state || {}

            // Keep a reference on the savingState at the time of this call.
            // This is important to compare it later in the setTimeout.
            let savingState = state.savingState

            if (!savingState) {
                return
            }

            //  A recovery was in progress, we must inform the user,
            //  and keep the savingState in the store
            if (savingState.recoveryState) {
                savingState.setRecoveryState(SAVING_RECOVERY_STATE.resolved)
                $monitoring.captureMessage(
                    `User ${rootState.users.me.id} has lost its websocket connection on item ${state.itemId} but recovered successfully`,
                )
                return
            }

            // The duration between now and the start of the loader display
            let ellapsedDuration = moment() - savingState.startTime
            // Ensure there's at least SAVING_MIN_DURATION of visible loader.
            setTimeout(() => {
                if (!state.savingState) {
                    return
                }

                // Clean the saving state only if there has not been another started in the interval
                if (state.savingState.id == savingState.id) {
                    commit("setSavingState", null)
                }
                // Will trigger immediatly if more than SAVING_LOADER_MIN_DURATION have ellapsed.
            }, Math.max(SAVING_LOADER_MIN_DURATION - ellapsedDuration, 0))
        },

        receiveItemContentChanges({ state, getters, commit, dispatch, rootState }, message) {
            let { editor, changes } = message
            for (let fieldName in changes || []) {
                let {
                    value,
                    version,
                    steps,
                    annotationsKey,
                    annotations,
                    clientId,
                    action,
                } = changes[fieldName]
                let isRemoteChange = clientId != state.myRealtimeClientId

                // The version we received is older than our current version, skip this change
                if (version <= state.fieldVersions[fieldName]) {
                    continue
                }

                let schema = getItemFieldSchema(state, fieldName)

                if (action != "addElasticElement" && schema && schema.is_prosemirror) {
                    // Confirm the version first, so we remove conflicting prosemirror steps from the unconfirmed changes.
                    commit("confirmVersion", { fieldName, version, isRemoteChange })

                    // We tell the tiptap editor to integrate the remote changes
                    let editor = state.tiptapEditors[fieldName]
                    if (editor && steps) {
                        // We receive the steps and integrate them into the editor.
                        // If our own document has evolved, this will rebase them as needed.
                        // When we rebase, this will trigger a complete input event chain from the TiptapEditor :
                        // receiveSteps -> dispatchTransaction -> onTransaction -> emitValueChange -> updateValue
                        // Which will in turn make the call to the store :
                        // setItemContentField + addPendingChange + saveItemContentRT
                        try {
                            editor.extensions.options.Collab.receiveSteps({ steps, clientId })
                        } catch (error) {
                            commit("users/popMessage", i18n.t("userMessages.receiveStepsError"), {
                                root: true,
                            })
                        }

                        // However, when we don't rebase ( most of the time ),
                        // ItemContentRichEditor.emitValueChange won't emit anything because there's no sendable steps.
                        // So we must keep our state in sync with the new value.
                        if (
                            !state.pendingChanges[fieldName] &&
                            !state.unconfirmedChanges[fieldName]
                        ) {
                            commit("setItemContentField", { fieldName, value: editor.getJSON() })
                            commit("setFieldAnnotations", { annotationsKey, annotations })
                        }
                    }
                } else {
                    // Remote changes, we need to check for conflicts
                    if (isRemoteChange) {
                        // Handle conflicts on non-prosemirror fields
                        if (
                            state.pendingChanges[fieldName] ||
                            state.unconfirmedChanges[fieldName]
                        ) {
                            commit("setConflictedField", { fieldName, value, editor })
                        }
                        // Integrate changes from other users
                        else {
                            commit("setItemContentField", { fieldName, value })
                        }
                    }
                    commit("confirmVersion", { fieldName, version, isRemoteChange })
                }

                // Set annotations only with remote changes, and when there's no steps
                // ( this will integrate remote annotation creation/edition ).
                //
                // If it's our own changes, we already have the latest data.
                // If it's a remote content changes ( with steps ),
                // we'll end up with the correct annotation positioning when rebasing.
                //
                // If we try to integrate remote annotation positioning,
                // it may trigger a rare bug on fast typing where the annotations positions
                // are erased and wrongly positioned.
                if (annotationsKey && annotations && isRemoteChange && !steps) {
                    commit("setFieldAnnotations", { annotationsKey, annotations })
                }
            }

            commit("setLastEditor", editor)
            commit("setLastEditionDatetime", new Date().toISOString())

            // If all our unconfirmed changes are now confirmed,
            // we are not saving anymore, stop the loader
            if (_.isEmpty(state.unconfirmedChanges)) {
                dispatch("endSaving")
            }
            // There was some pending changes waiting confirmation,
            // we can now send them.
            if (!_.isEmpty(state.pendingChanges)) {
                dispatch("saveItemContentRT")
            }
        },

        receiveRealtimeUsers({ state, commit, dispatch }, realtimeUsers) {
            // If the user were in the realtimeUsers list, but is not anymore,
            // that means the server has disconnected us because we were inactive.
            let wasConnected = _.find(state.realtimeUsers, { id: state.myRealtimeUser.id }),
                isStillConnected = _.find(realtimeUsers, { id: state.myRealtimeUser.id })
            if (wasConnected && !isStillConnected) {
                state.isDisconnectedAfterInactivity = true
                commit("throttledSetRealtimeUsers", [])
            } else {
                commit("throttledSetRealtimeUsers", realtimeUsers)
            }
        },

        checkForRecovery({ state, commit, dispatch, rootState }, savingState) {
            // state may be null because endSaving may be called in a setTimeout after we left the current page
            state = state || {}

            if (
                _.isEmpty(state.unconfirmedChanges) ||
                !state.savingState ||
                savingState.id != state.savingState.id ||
                state.savingState.isResolved
            ) {
                // Nominal case :
                // - no more unconfirmed changes, or
                // - another save is in progress, or
                // - recovery has been resolved
                //
                // All right, nothing to see here gentlemens.
                return
            }

            // The save is still in progress, not good.

            // First recovery step : try a new websocket connection
            if (!state.savingState.recoveryState) {
                state.savingState.setRecoveryState(SAVING_RECOVERY_STATE.reconnecting)

                // Verify again after 6 seconds
                setTimeout(
                    () => dispatch("checkForRecovery", savingState),
                    SAVING_VERIFICATION_DELAY,
                )

                realtime.reconnect()
                realtime.connectPromise.then(() => {
                    realtime.registerOnItem(state.itemId)

                    realtime.updateItemContent(
                        state.unconfirmedChanges,
                        null, // pending selection has been lost after the first attempt, but that's not very important
                    )
                })
            }

            // Second recovery step : try a, XHR connection
            else if (state.savingState.isReconnecting) {
                state.savingState.setRecoveryState(SAVING_RECOVERY_STATE.xhr)

                // Verify again after 6 seconds
                setTimeout(
                    () => dispatch("checkForRecovery", savingState),
                    SAVING_VERIFICATION_DELAY,
                )

                dispatch("updateItemContentWithXhr", state.unconfirmedChanges)
            }

            // None of the recovery attempts were succesful, we failed :-(
            else {
                state.savingState.setRecoveryState(SAVING_RECOVERY_STATE.failed)
                $monitoring.captureMessage(
                    `User ${rootState.users.me.id} has lost its websocket connection on item ${state.itemId} and failed to recover`,
                )
            }
        },

        sendItemContentChanges({ state, commit, dispatch }) {
            // This may happen if we discarded the pendingChanges in the interval
            // after adding them ( because we received some conflicting changes )
            if (_.isEmpty(state.pendingChanges)) {
                return
            }
            // Don't send some new changes while there's still some unconfirmed changes.
            if (!_.isEmpty(state.unconfirmedChanges)) {
                return
            }

            let savingState = new ItemSavingState()
            commit("setSavingState", savingState)
            // Prepare the versions on the pending changes
            commit("preparePendingChangesForSending")

            if (realtime.state == realtime.STATES.CLOSED) {
                // there's an error with the realtime server,
                // we must fallback on http call
                dispatch("updateItemContentWithXhr", state.pendingChanges)
            } else {
                // Verify if recovery is needed after 6 seconds
                setTimeout(
                    () => dispatch("checkForRecovery", savingState),
                    SAVING_VERIFICATION_DELAY,
                )

                // Nominal case :  send through websocket
                realtime.updateItemContent(state.pendingChanges, state.pendingSelection)
            }
            // Clear the pending changes
            commit("pendingChangesHaveBeenSent")
        },

        throttledSendItemContentChanges: _.throttle(
            ({ dispatch }) => {
                dispatch("sendItemContentChanges")
            },
            SAVING_THROTTLE_TIME,
            {
                leading: false,
                trailing: true,
            },
        ),

        saveItemContentRT({ state, dispatch }) {
            dispatch("throttledSendItemContentChanges")
        },

        updateItemContentWithXhr({ state, commit, dispatch, rootState }, changes) {
            $http({
                method: "PUT",
                url: urls.itemUpdateContent.format({ id: state.itemId }),
                data: { changes },
            })
                .then((response) => {
                    let message = response.data
                    commit("setDesynchronized", message.desynchronized)
                    if (!_.isEmpty(message.accepted_changes)) {
                        // Simulate an event as if received through the realtime channel.
                        // This will trigger ItemContentFormStore.receiveItemContentChanges()
                        // and also ItemStore.receiveLatestSession()
                        realtime.callMessageHandlers({
                            type: realtime.S2C_MESSAGES.BROADCAST_ITEM_CHANGES,
                            changes: message.accepted_changes,
                            session: message.session,
                            editor: rootState.users.me,
                        })
                    }
                })
                .catch(() => {
                    commit("setDesynchronized", true)
                })
        },

        conflictAcceptMine({ state, commit, dispatch }, fieldName) {
            commit("addPendingChange", { fieldName, value: state.itemEditable.content[fieldName] })
            dispatch("saveItemContentRT")
            commit("resolveConflictedField", fieldName)
        },
        conflictAcceptTheirs({ state, commit, dispatch }, fieldName) {
            let conflict = state.conflictedFields[fieldName]
            commit("setItemContentField", { fieldName, value: conflict.value })
            commit("resolveConflictedField", fieldName)
        },

        /**
         * To prevent multiple annotation boxes to be displayed,
         * we deselect all annotations from the annotation managers,
         * and we also cancel all annotation in creation.
         */
        deselectAllAnnotations({ state, commit, dispatch }, { exclude } = {}) {
            for (let annotationManager of Object.values(state.annotationManagers)) {
                if (annotationManager != exclude) {
                    annotationManager.deselectAnnotations()
                }
            }
        },

        alertBase64Image({ commit }) {
            commit("users/popMessage", i18n.t("userMessages.alertBase64Image"), { root: true })
        },
    },
}
