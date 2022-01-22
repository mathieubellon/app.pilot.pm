import DashboardStore from "./modules/DashboardStore.js"

import ProjectListStore from "./modules/ProjectListStore.js"
import ProjelDetailStore from "./modules/ProjelDetailStore.js"

import ItemActionsStore from "./modules/ItemActionsStore"
import ItemListStore from "./modules/ItemListStore"
import ItemCalendarStore from "./modules/ItemCalendarStore"
import ItemDetailStore from "./modules/ItemDetailStore"
import ItemContentFormStore from "./modules/ItemContentFormStore.js"

import ChannelListStore from "./modules/ChannelListStore.js"

import AssetListStore from "./modules/AssetListStore.js"
import AssetDetailStore from "./modules/AssetDetailStore.js"

import WikiStore from "@/store/modules/WikiStore.js"

import LabelStore from "./modules/LabelStore.js"

import ItemTypeAdminStore from "./modules/ItemTypeAdminStore.js"
import TaskGroupAdminStore from "./modules/TaskGroupAdminStore.js"
import WorkflowStore from "./modules/WorkflowStore.js"
import UsersAdminStore from "./modules/UsersAdminStore.js"
import DeskAdminStore from "./modules/DeskAdminStore.js"

export default {
    modules: {
        dashboard: DashboardStore,

        projelDetail: ProjelDetailStore,

        projectList: ProjectListStore,
        channelList: ChannelListStore,

        itemActions: ItemActionsStore,
        itemList: ItemListStore,
        calendar: ItemCalendarStore,
        itemDetail: ItemDetailStore,
        itemContentForm: ItemContentFormStore,

        assetList: AssetListStore,
        assetDetail: AssetDetailStore,

        wiki: WikiStore,

        labels: LabelStore,

        itemTypes: ItemTypeAdminStore,
        taskGroup: TaskGroupAdminStore,
        workflow: WorkflowStore,
        usersAdmin: UsersAdminStore,
        desk: DeskAdminStore,
    },
    state: {
        objectNotFound: false,
    },
    mutations: {
        setObjectNotFound(state, objectNotFound) {
            state.objectNotFound = objectNotFound
        },
    },
    getters: {
        currentRouteName(state, getters, rootState) {
            return rootState.route ? rootState.route.name : null
        },
    },
}
