import Vue from "vue"
import urls from "@js/urls"
import { $httpX } from "@js/ajax.js"
import i18n from "@js/i18n"
import { EVENTS, dispatchEvent } from "@js/events"

export const DEFAULT_LABEL_COLOR = "#263238"
export const DEFAULT_LABEL_BG_COLOR = "#CFD8DC"

// For now, target types are statically defined.
// In the future, they should be user-defined
const TARGET_TYPES_SPEC = []
function createTargetTypeSpec(name, model, fieldName, fieldNamePlural, sortable) {
    TARGET_TYPES_SPEC.push({ name, model, fieldName, fieldNamePlural, sortable })
}
// createTargetType('asset_tags', i18n.t('asset'), i18n.t('tags'))
createTargetTypeSpec(
    "asset_right_medium",
    i18n.t("assetRight"),
    i18n.t("assetMedium"),
    i18n.t("assetMediums"),
    true,
)
createTargetTypeSpec(
    "asset_folder",
    i18n.t("asset"),
    i18n.t("assetFolder"),
    i18n.t("assetFolders"),
    true,
)
createTargetTypeSpec("channel_type", i18n.t("channel"), i18n.t("type"), i18n.t("types"), true)
createTargetTypeSpec("item_tags", i18n.t("item"), i18n.t("tag"), i18n.t("tags"), false)
createTargetTypeSpec(
    "project_category",
    i18n.t("project"),
    i18n.t("category"),
    i18n.t("categories"),
    true,
)
createTargetTypeSpec(
    "project_priority",
    i18n.t("project"),
    i18n.t("priority"),
    i18n.t("priorities"),
    true,
)
createTargetTypeSpec("project_tags", i18n.t("project"), i18n.t("tag"), i18n.t("tags"), false)

export default {
    namespaced: true,
    state: {
        targetTypeSpecs: TARGET_TYPES_SPEC,
        // {targetType: [List of labels]}
        labels: {},
    },
    mutations: {
        setLabels(state, { targetType, labels }) {
            Vue.set(state.labels, targetType, labels)
        },
        appendToLabels(state, label) {
            state.labels[label.target_type].push(label)
        },
        updateLabel(state, label) {
            state.labels[label.target_type] = state.labels[label.target_type].map((oldLabel) =>
                oldLabel.id == label.id ? label : oldLabel,
            )
        },
        removeLabel(state, label) {
            state.labels[label.target_type] = state.labels[label.target_type].filter(
                (l) => l.id != label.id,
            )
        },
    },
    actions: {
        fetchLabels({ state, commit }, targetType) {
            return $httpX({
                commit,
                name: "fetchLabels",
                method: "GET",
                url: urls.labels,
                params: { target_type: targetType },
            }).then((response) => {
                commit("setLabels", { targetType, labels: response.data })
            })
        },
        createLabel({ state, commit }, label) {
            return $httpX({
                commit,
                name: "createLabel",
                method: "POST",
                url: urls.labels,
                data: label,
            }).then((response) => {
                commit("appendToLabels", response.data)
                return response.data
            })
        },
        partialUpdateLabel({ state, commit, dispatch }, labelData) {
            return $httpX({
                name: "partialUpdateLabel",
                commit,
                url: urls.labels.format({ id: labelData.id }),
                method: "PATCH",
                data: labelData,
            }).then((response) => {
                let label = response.data
                commit("updateLabel", label)
                dispatchEvent(EVENTS.labelUpdated, label)
                return label
            })
        },
        setLabelsOrder({ state, commit }, { targetType, labelOrder }) {
            $httpX({
                commit,
                name: "setLabelsOrder",
                method: "POST",
                url: urls.labelsSetOrder,
                data: labelOrder,
            }).then((response) => {
                commit("setLabels", { targetType, labels: response.data })
            })
        },
        deleteLabel({ state, commit, dispatch }, label) {
            $httpX({
                name: "deleteLabel",
                commit,
                url: urls.labels.format({ id: label.id }),
                method: "DELETE",
            }).then((response) => {
                // Remove the label from the list
                commit("removeLabel", label)
                // Notify other stores of the removal
                dispatchEvent(EVENTS.labelDeleted, label)
            })
        },
    },
}
