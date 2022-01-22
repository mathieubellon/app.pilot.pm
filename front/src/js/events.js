import _ from "lodash"
import { mainApp } from "@js/bootstrap"
import Emitter from "@js/Emitter"

export const EVENTS = {
    itemCreated: "itemCreated",
    itemUpdated: "itemUpdated",
    itemTrashed: "itemTrashed",

    itemBulkUpdated: "itemBulkUpdated",
    itemBulkTrashed: "itemBulkTrashed",
    itemBulkCopied: "itemBulkCopied",
    itemBulkRemovedFromProjel: "itemBulkRemovedFromProjel",

    labelUpdated: "labelUpdated",
    labelDeleted: "labelDeleted",

    projectCreated: "projectCreated",
    projectUpdated: "projectUpdated",
    projectClosed: "projectClosed",
    projectDeleted: "projectDeleted",

    taskCreated: "taskCreated",
    taskUpdated: "taskUpdated",
    taskDeleted: "taskDeleted",

    channelCreated: "channelCreated",
    channelUpdated: "channelUpdated",
    channelClosed: "channelClosed",
    channelDeleted: "channelDeleted",

    assetCreated: "assetCreated",
    assetUpdated: "assetUpdated",
    assetDeleted: "assetDeleted",

    targetCreated: "targetCreated",
    targetUpdated: "targetUpdated",
    targetDeleted: "targetDeleted",

    workflowStateCreated: "workflowStateCreated",
    workflowStateUpdated: "workflowStateUpdated",
    workflowStateDeleted: "workflowStateDeleted",
    workflowStateSorted: "workflowStateSorted",

    userInvited: "userInvited",
    userDeinvited: "userDeinvited",
    userDeactivated: "userDeactivated",
    userReactivated: "userReactivated",

    teamCreated: "teamCreated",
    teamUpdated: "teamUpdated",
    teamDeleted: "teamDeleted",
}

export const eventBus = new Emitter()

export function dispatchEvent(eventName, payload) {
    if (!(eventName in EVENTS)) {
        throw Error(`${eventName} is not an event name`)
    }
    mainApp.$store.dispatch(eventName, payload)
    eventBus.emit(eventName, payload)
}

export function mapEvents(handlers) {
    return _.mapValues(handlers, (handler) => ({
        root: true,
        handler,
    }))
}
