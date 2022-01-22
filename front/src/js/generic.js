import _ from "lodash"
import i18n from "@js/i18n"

import { SharingType } from "@/store/PublicSharingStore"

const GLOModels = {
    ASSET: "Asset",
    ASSET_RIGHT: "AssetRight",
    CHANNEL: "Channel",
    COMMENT: "Comment",
    EDIT_SESSION: "EditSession",
    ITEM: "Item",
    ITEM_FEEDBACK: "ItemFeedback",
    INTERNAL_SHARED_FILTER: "InternalSharedFilter",
    SAVED_FILTER: "SavedFilter",
    PROJECT: "Project",
    SHARING: "Sharing",
    TASK: "Task",
    WIKI_PAGE: "WikiPage",
}

i18n.mergeLocaleMessage("fr", {
    unknownObject: "Object indéterminé",
})
i18n.mergeLocaleMessage("en", {
    unknownObject: "Unknown object",
})

function getTaskRepr(task) {
    if (task.item) {
        return `${task.name} ( ${task.item.title} )`
    }
    if (task.project) {
        return `${task.name} ( ${task.project.name} )`
    }
    return task.name
}

function getSharingTarget(sharing) {
    try {
        switch (sharing.type) {
            case SharingType.CHANNEL:
                return i18n.t("channel") + " " + sharing.channel.name
            case SharingType.ITEM:
                return i18n.t("item") + " " + sharing.item.title
            case SharingType.PROJECT:
                return i18n.t("project") + " " + sharing.project.name
            case SharingType.CALENDAR:
            case SharingType.LIST:
                return i18n.t("savedFilter") + " " + sharing.saved_filter.title
        }
    } catch {
        return "?"
    }
}

/***
 * Transform a serialized Generic Linked Object (GLO)
 * into a representation string
 *
 * @param glo Generic Linked Object
 */
function getGLORepr(glo) {
    let modelName = _.get(glo, "model_name")
    let instance = _.get(glo, "details")

    if (modelName && instance) {
        switch (modelName) {
            case GLOModels.ASSET:
                return i18n.t("asset") + " " + instance.title
            case GLOModels.ASSET_RIGHT:
                return i18n.t("asset") + " " + instance.asset.title
            case GLOModels.CHANNEL:
                return i18n.t("channel") + " " + instance.name
            case GLOModels.COMMENT:
                return i18n.t("comment") + " " + instance.name
            case GLOModels.EDIT_SESSION:
                return i18n.t("version") + " " + instance.version
            case GLOModels.ITEM:
                return i18n.t("item") + " " + instance.title
            case GLOModels.ITEM_FEEDBACK:
                return i18n.t("sharing") + " " + getSharingTarget(instance.sharing)
            case GLOModels.INTERNAL_SHARED_FILTER:
                return i18n.t("savedFilter") + " " + instance.saved_filter.title
            case GLOModels.SAVED_FILTER:
                return i18n.t("savedFilter") + " " + instance.title
            case GLOModels.PROJECT:
                return i18n.t("project") + " " + instance.name
            case GLOModels.SHARING:
                return i18n.t("sharing") + " " + getSharingTarget(instance)
            case GLOModels.TASK:
                return i18n.t("task") + " " + instance.name
            case GLOModels.WIKI_PAGE:
                return i18n.t("wikiPage") + " " + instance.name
            default:
                return i18n.t("unknownObject")
        }
    }
}

export { GLOModels, getTaskRepr, getSharingTarget, getGLORepr }
