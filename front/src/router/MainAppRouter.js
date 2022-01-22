import i18n from "@js/i18n"

import MyDashboard from "@views/dashboard/MyDashboard.vue"
import Notifications from "@views/notifications/panel/Notifications.vue"
import MyTasks from "@views/tasks/myTasksPanel/MyTasks"
import Favorites from "@views/favorites/Favorites"
import Search from "@views/search/SearchPanel"

import ProjelDetailApp from "@views/projel/detail/ProjelDetailApp.vue"
import ProjelDetailContents from "@views/projel/detail/ProjelDetailContents.vue"
import ProjelDetailHierarchy from "@views/projel/detail/ProjelDetailHierarchy.vue"
import ProjelDetailActivity from "@views/projel/detail/ProjelDetailActivity.vue"
import ProjelDetailLinkedAssets from "@views/projel/detail/ProjelDetailLinkedAssets.vue"
import ProjelDetailInformations from "@views/projel/detail/ProjelDetailInformations.vue"
import ProjelDetailTasks from "@views/projel/detail/ProjelDetailTasks.vue"

import ProjectListApp from "@views/projects/list/ProjectListApp.vue"
import ProjectList from "@views/projects/list/ProjectList"

import ItemListApp from "@views/items/list/ItemListApp"
import ItemListWithBigFilter from "@views/items/list/ItemListWithBigFilter"
import ItemCalendarApp from "@views/items/calendar/ItemCalendarApp"
import ItemCalendar from "@views/items/calendar/ItemCalendar"
import ItemDetailApp from "@views/items/detail/ItemDetailApp"

import ChannelListApp from "@views/channels/list/ChannelListApp.vue"
import ChannelList from "@views/channels/list/ChannelList"

import AssetListApp from "@views/assets/list/AssetListApp"
import AssetList from "@views/assets/list/AssetList"
import AssetDetailApp from "@views/assets/detail/AssetDetailApp"
import AssetDetailInformations from "@views/assets/detail/AssetDetailInformations"
import AssetDetailRights from "@views/assets/detail/AssetDetailRights"

import WikiApp from "@views/wiki/WikiApp.vue"
import WikiPage from "@views/wiki/WikiPage.vue"

import TargetAdminApp from "@views/targets/TargetAdminApp.vue"

import LabelAdminApp from "@views/labels/admin/LabelAdminApp.vue"
import LabelTargetTypeList from "@views/labels/admin/LabelTargetTypeList.vue"
import LabelsList from "@views/labels/admin/LabelsList.vue"

import ItemTypeAdminApp from "@views/itemTypes/ItemTypeAdminApp.vue"
import ItemTypeList from "@views/itemTypes/ItemTypeList.vue"
import ItemTypeEdit from "@views/itemTypes/ItemTypeEdit.vue"

import TaskGroupAdminApp from "@views/tasks/taskGroup/TaskGroupAdminApp.vue"
import TaskGroupList from "@views/tasks/taskGroup/TaskGroupList.vue"
import TaskGroupDetail from "@views/tasks/taskGroup/TaskGroupDetail.vue"

import WorkflowStateAdminApp from "@views/workflow/WorkflowStateAdminApp.vue"

import TokenAdminApp from "@views/integrations/TokenAdminApp.vue"

import SharingAdminApp from "@views/sharings/admin/SharingAdminApp.vue"

import UserAdminApp from "@views/users/admin/UserAdminApp.vue"
import UserList from "@views/users/admin/UserList.vue"
import TeamList from "@views/users/admin/TeamList.vue"
import TeamDetail from "@views/users/admin/TeamDetail.vue"

import DeskApp from "@views/desk/admin/DeskApp.vue"
import DeskEdit from "@views/desk/admin/DeskEdit.vue"
import DeskConfig from "@views/desk/admin/DeskConfig.vue"
import DeskExport from "@views/desk/admin/DeskExport.vue"

import SubscriptionApp from "@views/SubscriptionApp"

import NotFoundComponent from "@components/NotFoundComponent.vue"

export default {
    mode: "history",
    routes: [
        {
            path: "/",
            name: "home",
            redirect: "dashboard",
        },
        {
            path: "/notifications",
            name: "notifications",
            component: Notifications,
            meta: {
                menu: "notifications",
                title: i18n.t("myNotifications"),
            },
        },
        {
            path: "/search",
            name: "search",
            component: Search,
            meta: {
                menu: "search",
                title: i18n.t("search"),
            },
        },
        {
            path: "/tasks",
            name: "myTasks",
            component: MyTasks,
            meta: {
                menu: "tasks",
                title: i18n.t("myTasks"),
            },
        },
        {
            path: "/favorites",
            name: "favorites",
            component: Favorites,
            meta: {
                menu: "favorites",
                title: i18n.t("myFavorites"),
            },
        },
        {
            path: "/dashboard",
            name: "dashboard",
            component: MyDashboard,
            meta: {
                menu: "dashboard",
                title: i18n.t("dashboard"),
            },
        },

        {
            path: "/projects",
            component: ProjectListApp,
            meta: {
                menu: "projects",
                title: i18n.t("projects"),
            },
            children: [
                { path: "", name: "projectList", redirect: "active" },
                {
                    path: "idea",
                    name: "projectList-idea",
                    component: ProjectList,
                },
                {
                    path: "active",
                    name: "projectList-active",
                    component: ProjectList,
                },
                {
                    path: "closed",
                    name: "projectList-closed",
                    component: ProjectList,
                },
            ],
        },
        {
            path: "/projects/:id",
            component: ProjelDetailApp,
            meta: {
                menu: "projects",
                title: i18n.t("projects"),
            },
            children: [
                {
                    path: "",
                    name: "projectDetail",
                    redirect: "informations",
                },
                {
                    path: "informations",
                    name: "projectDetail-informations",
                    component: ProjelDetailInformations,
                },
                {
                    path: "contents",
                    name: "projectDetail-contents",
                    component: ProjelDetailContents,
                },
                {
                    path: "hierarchy",
                    name: "projectDetail-hierarchy",
                    component: ProjelDetailHierarchy,
                },
                {
                    path: "activity",
                    name: "projectDetail-activity",
                    component: ProjelDetailActivity,
                },
                {
                    path: "assets",
                    name: "projectDetail-assets",
                    component: ProjelDetailLinkedAssets,
                },
                {
                    path: "tasks",
                    name: "projectDetail-tasks",
                    component: ProjelDetailTasks,
                },
            ],
        },

        {
            path: "/items",
            component: ItemListApp,
            meta: {
                menu: "items",
                title: i18n.t("items"),
            },
            children: [
                { path: "", name: "itemList", redirect: "active" },
                {
                    path: "active",
                    name: "itemList-active",
                    component: ItemListWithBigFilter,
                },
                {
                    path: "trash",
                    name: "itemList-trash",
                    component: ItemListWithBigFilter,
                },
                {
                    path: "filter/:id",
                    name: "itemList-filter",
                    component: ItemListWithBigFilter,
                },
            ],
        },
        {
            path: "/items/calendar",
            component: ItemCalendarApp,
            meta: {
                menu: "calendar",
                title: i18n.t("calendars"),
            },
            children: [
                {
                    path: "",
                    name: "calendar",
                    redirect: "main",
                },
                {
                    path: "main",
                    name: "calendar-main",
                    component: ItemCalendar,
                },
                {
                    path: "filter/:id",
                    name: "calendar-filter",
                    component: ItemCalendar,
                },
            ],
        },
        {
            path: "/items/types",
            component: ItemTypeAdminApp,
            meta: {
                menu: "admin",
                title: i18n.t("itemsTypes"),
            },
            children: [
                {
                    path: "/",
                    name: "itemTypesList",
                    component: ItemTypeList,
                },
                {
                    path: ":id",
                    name: "itemTypesEdit",
                    component: ItemTypeEdit,
                },
            ],
        },
        {
            path: "/items/:id",
            name: "itemDetail",
            component: ItemDetailApp,
            meta: {
                menu: "items",
                title: i18n.t("items"),
            },
        },

        {
            path: "/channels",
            component: ChannelListApp,
            meta: {
                menu: "channels",
                title: i18n.t("channels"),
            },
            children: [
                { path: "", name: "channelList", redirect: "active" },
                {
                    path: "active",
                    name: "channelList-active",
                    component: ChannelList,
                },
                {
                    path: "closed",
                    name: "channelList-closed",
                    component: ChannelList,
                },
            ],
        },
        {
            path: "/channels/:id",
            component: ProjelDetailApp,
            meta: {
                menu: "channels",
                title: i18n.t("channels"),
            },
            children: [
                { path: "", name: "channelDetail", redirect: "informations" },
                {
                    path: "informations",
                    name: "channelDetail-informations",
                    component: ProjelDetailInformations,
                },
                {
                    path: "contents",
                    name: "channelDetail-contents",
                    component: ProjelDetailContents,
                },
                {
                    path: "hierarchy",
                    name: "channelDetail-hierarchy",
                    component: ProjelDetailHierarchy,
                },
                {
                    path: "activity",
                    name: "channelDetail-activity",
                    component: ProjelDetailActivity,
                },
                {
                    path: "assets",
                    name: "channelDetail-assets",
                    component: ProjelDetailLinkedAssets,
                },
                {
                    path: "tasks",
                    name: "channelDetail-tasks",
                    component: ProjelDetailTasks,
                },
            ],
        },

        {
            path: "/assets",
            component: AssetListApp,
            meta: {
                menu: "assets",
                title: i18n.t("assets"),
            },
            children: [
                {
                    path: "/",
                    name: "assetList",
                    component: AssetList,
                },
            ],
        },

        {
            path: "/assets/:id",
            component: AssetDetailApp,
            meta: {
                menu: "assets",
                title: i18n.t("assets"),
            },
            children: [
                { path: "", name: "assetDetail", redirect: "informations" },
                {
                    path: "informations",
                    name: "informations",
                    component: AssetDetailInformations,
                },
                {
                    path: "usageRights",
                    name: "usageRights",
                    component: AssetDetailRights,
                },
            ],
        },

        {
            path: "/wiki",
            component: WikiApp,
            meta: {
                menu: "wiki",
                title: i18n.t("wiki"),
            },
            children: [
                {
                    path: "/",
                    name: "wikiHome",
                    component: WikiPage,
                },
                {
                    path: ":id",
                    name: "wikiPage",
                    component: WikiPage,
                },
            ],
        },

        {
            path: "/targets",
            name: "targets",
            component: TargetAdminApp,
            meta: {
                menu: "admin",
                title: i18n.t("targets"),
            },
        },

        {
            path: "/labels",
            component: LabelAdminApp,
            meta: {
                menu: "admin",
                title: i18n.t("labels"),
            },
            children: [
                {
                    path: "/",
                    name: "labels",
                    component: LabelTargetTypeList,
                },
                {
                    path: ":targetType",
                    name: "labelsList",
                    component: LabelsList,
                },
            ],
        },

        {
            path: "/tasks/groups",
            component: TaskGroupAdminApp,
            meta: {
                menu: "admin",
                title: i18n.t("taskGroup"),
            },
            children: [
                {
                    path: "/",
                    name: "taskGroupList",
                    component: TaskGroupList,
                },
                {
                    path: ":id",
                    name: "taskGroupDetails",
                    component: TaskGroupDetail,
                },
            ],
        },

        {
            path: "/workflow/states",
            name: "workflowState",
            component: WorkflowStateAdminApp,
            meta: {
                menu: "admin",
                title: i18n.t("workflowStates"),
            },
        },

        {
            path: "/integrations/tokens/",
            name: "integrations",
            component: TokenAdminApp,
            meta: {
                menu: "admin",
                title: i18n.t("integrations"),
            },
        },

        {
            path: "/sharings/",
            name: "sharings",
            component: SharingAdminApp,
            meta: {
                menu: "admin",
                title: i18n.t("sharings"),
            },
        },

        {
            path: "/users",
            component: UserAdminApp,
            meta: {
                menu: "admin",
                title: i18n.t("users"),
            },
            children: [
                { path: "/", redirect: "/users/actives" },
                {
                    path: "actives",
                    name: "actives",
                    component: UserList,
                },
                {
                    path: "inactives",
                    name: "inactives",
                    component: UserList,
                },
                {
                    path: "pending",
                    name: "pending",
                    component: UserList,
                },
                {
                    path: "teams",
                    name: "teams",
                    component: TeamList,
                },
                {
                    path: "teams/:id",
                    name: "teamDetail",
                    component: TeamDetail,
                },
            ],
        },

        {
            path: "/desk",
            component: DeskApp,
            meta: {
                menu: "admin",
                title: i18n.t("desk"),
            },
            children: [
                { path: "/", redirect: "/desk/edit" },
                {
                    path: "edit",
                    name: "edit",
                    component: DeskEdit,
                },
                {
                    path: "config",
                    name: "config",
                    component: DeskConfig,
                },
                {
                    path: "export",
                    name: "export",
                    component: DeskExport,
                },
            ],
        },

        {
            path: "/subscription",
            name: "subscription",
            component: SubscriptionApp,
        },

        {
            path: "*",
            name: "404",
            component: NotFoundComponent,
        },
    ],
}
