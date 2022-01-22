import _ from "lodash"
import urls from "@js/urls"
import Vue from "vue"
import { $httpX } from "@js/ajax.js"
import i18n from "@js/i18n"

const ITEM_LIST_COLUMNS_SPEC = [
    {
        name: "itemType",
        default: true,
        label: i18n.t("type"),
    },
    {
        name: "id",
        default: true,
        label: i18n.t("id"),
    },
    {
        name: "title",
        required: true,
        default: true,
        label: i18n.t("title"),
    },
    {
        name: "language",
        default: true,
        label: i18n.t("language"),
    },
    {
        name: "publication",
        default: true,
        label: i18n.t("publication"),
    },
    {
        name: "project",
        default: true,
        label: i18n.t("project"),
    },
    {
        name: "channels",
        default: true,
        label: i18n.t("channels"),
    },
    {
        name: "state",
        default: true,
        label: i18n.t("state"),
    },
]

const LIST_CONFIG_BASE_NAMES = {
    ItemList: "ItemList",
    ItemListForProject: "ItemListForProject",
    ItemListForChannel: "ItemListForChannel",
}

function getListName(baseName, objectId) {
    if (!_.includes(LIST_CONFIG_BASE_NAMES, baseName)) {
        throw Error("Incorrect base name : " + baseName)
    }
    return objectId ? baseName + "-" + objectId : baseName
}

export function getMainItemListName() {
    return getListName(LIST_CONFIG_BASE_NAMES.ItemList)
}

export function getItemListForProjectName(projectId) {
    return getListName(LIST_CONFIG_BASE_NAMES.ItemListForProject, projectId)
}

export function getItemListForChannelName(channelId) {
    return getListName(LIST_CONFIG_BASE_NAMES.ItemListForChannel, channelId)
}

export default {
    namespaced: true,
    state: {
        ITEM_LIST_COLUMNS_SPEC: ITEM_LIST_COLUMNS_SPEC,
        listConfigs: {},
    },
    mutations: {
        setListConfig(state, { name, listConfig }) {
            Vue.set(state.listConfigs, name, listConfig)
        },
        setColumnsConfig(state, columns) {
            let mainConfig = state.listConfigs[getMainItemListName()]
            if (!mainConfig) {
                return
            }
            mainConfig.columns = columns
        },
    },
    getters: {
        itemListColumns: (state) => {
            let listName = getMainItemListName()
            let columns = {}
            if (state.listConfigs[listName] && state.listConfigs[listName].columns) {
                columns = state.listConfigs[listName].columns
            }
            for (let columnSpec of ITEM_LIST_COLUMNS_SPEC) {
                if (!columns.hasOwnProperty(columnSpec.name)) {
                    columns[columnSpec.name] = columnSpec.default
                }
            }
            return columns
        },
    },
    actions: {
        fetchListConfig({ commit, rootState }, name) {
            let urlParams = { name },
                listConfigUrl = urls.listConfig
            if (rootState.sharing) {
                listConfigUrl = urls.listConfigShared
                urlParams.token = rootState.sharing.token
            }

            return $httpX({
                name: "fetchListConfig",
                commit,
                url: listConfigUrl.format(urlParams),
            }).then((response) => {
                commit("setListConfig", {
                    name: name,
                    listConfig: response.data,
                })
                return response.data
            })
        },
        partialUpdateListConfig({ commit }, { name, listConfig }) {
            $httpX({
                name: "partialUpdateListConfig",
                method: "PATCH",
                commit,
                url: urls.listConfig.format({ name }),
                data: listConfig,
            }).then((response) => {
                commit("setListConfig", {
                    name: name,
                    listConfig: response.data,
                })
                return response.data
            })
        },
    },
}
