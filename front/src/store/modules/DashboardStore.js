import _ from "lodash"
import urls from "@js/urls"
import { $httpX } from "@js/ajax.js"
import i18n from "@js/i18n"
import { getFileProperties } from "@js/assetsUtils.js"

import ActivityFeedStore from "@/store/modules/ActivityFeedStore.js"

i18n.mergeLocaleMessage("fr", {
    activities: "Flux d'activités",
    activitiesDescription: "Toutes les actions des utilisateurs de la plateforme",
    allProjects: "Tous les projets actifs",
    allProjectsDescription: "Tous les projets actifs, quel que soit le responsable",
    filteredItems: "{title}",
    filteredItemsDescription:
        "Liste de contenus, filtrée à partir de votre filtre sauvegardé {title}",
    myItems: "Mes contenus",
    myItemsDescription:
        "Contenus dont je suis responsable, triés par date de mise à jour la plus récente en premier",
    myItemsToPublishSoon: "Mes contenus à publier prochainement",
    myItemsToPublishSoonDescription:
        "Contenus dont je suis reponsable et dont la date de publication est dans les 7 prochains jours",
    myProjects: "Mes projets (responsable)",
    myProjectsDescription:
        "Projets actifs dont je suis responsable, triés par date de mise à jour la plus récente en premier",
    myProjectsAsMember: "Mes projets (membre)",
    myProjectsAsMemberDescription:
        "Projets actifs dont je suis membre, triés par date de mise à jour la plus récente en premier",
})
i18n.mergeLocaleMessage("en", {
    activities: "Activity feed",
    activitiesDescription: "All the actions of the users of the platform",
    allProjects: "All actives projects",
    allProjectsDescription: "All actives projects, whoever is responsible",
    filteredItems: "{title}",
    filteredItemsDescription: "Contents list, filtered from you saved filter {title}",
    myItems: "My contents",
    myItemsDescription:
        "Content for which I am responsible, sorted by most recent update date first",
    myItemsToPublishSoon: "My contents to publish soon",
    myItemsToPublishSoonDescription:
        "Contents of which I am responsible and whose publication date is in the next 7 days",
    myProjects: "My Projects (owner)",
    myProjectsDescription:
        "Active projects for which I am responsible, sorted by most recent update date first",
    myProjectsAsMember: "My Projects (member)",
    myProjectsAsMemberDescription:
        "Active projects for which I am member, sorted by most recent update date first",
})

let staticTiles = [
    {
        name: "allProjects",
        type: "TileProjectList",
        title: i18n.t("allProjects"),
        description: i18n.t("allProjectsDescription"),
        queryParams: {
            order_by: "-updated_at",
        },
        filterOwnersOnUserMe: false,
        params: {},
        isBuiltIn: true,
    },
    {
        name: "myProjects",
        type: "TileProjectList",
        title: i18n.t("myProjects"),
        description: i18n.t("myProjectsDescription"),
        queryParams: {
            order_by: "-updated_at",
        },
        filterOwnersOnUserMe: true,
        params: {},
        isBuiltIn: true,
    },
    {
        name: "myProjectsAsMember",
        type: "TileProjectList",
        title: i18n.t("myProjectsAsMember"),
        description: i18n.t("myProjectsAsMemberDescription"),
        queryParams: {
            order_by: "-updated_at",
        },
        filterMembersOnUserMe: true,
        params: {},
        isBuiltIn: true,
    },
    {
        name: "myItems",
        type: "TileItemList",
        title: i18n.t("myItems"),
        description: i18n.t("myItemsDescription"),
        queryParams: {
            order_by: "-updated_at",
        },
        filterOwnersOnUserMe: true,
        params: {},
        isBuiltIn: true,
    },
    {
        name: "myItemsToPublishSoon",
        type: "TileItemList",
        title: i18n.t("myItemsToPublishSoon"),
        description: i18n.t("myItemsToPublishSoonDescription"),
        queryParams: {
            order_by: "-updated_at",
            period: 168,
        },
        filterOwnersOnUserMe: true,
        params: {},
        isBuiltIn: true,
    },
    {
        name: "activities",
        type: "TileActivityFeed",
        title: i18n.t("activities"),
        description: "Toutes les actions des utilisateurs de la plateforme",
        queryParams: {
            order_by: "-updated_at",
        },
        params: {},
        isBuiltIn: true,
    },
]

export default {
    namespaced: true,
    modules: {
        activityFeed: ActivityFeedStore,
    },
    state: {},
    mutations: {},
    getters: {
        // All the tiles available to this user, as a list
        allTilesAvailable(state, getters, rootState) {
            let savedFilters = rootState.savedFilter.savedFilters
            return _.concat(
                staticTiles,
                savedFilters.map((savedFilter) => ({
                    name: "savedFilter-" + savedFilter.id,
                    type: "TileItemList",
                    title: i18n.t("filteredItems", { title: savedFilter.title }),
                    description: i18n.t("filteredItemsDescription", { title: savedFilter.title }),
                    queryParams: savedFilter.query,
                    params: {
                        id: savedFilter.id,
                    },
                    isBuiltIn: false,
                })),
            )
        },
        // All the tiles available to this user, as a map { 'name': tile }
        allTilesByName(state, getters) {
            return _.keyBy(getters.allTilesAvailable, "name")
        },
        // The tiles that can still be added by the user (not already added to the dashboard)
        tilesRemaining(state, getters) {
            return _.differenceBy(getters.allTilesAvailable, getters.userTilesConfig, "name")
        },

        // The tiles added by the user, in the format
        // [ { name: 'tileName', params: {...} }, ... ]
        userTilesConfig(state, getters, rootState) {
            return (
                _.get(rootState.users.me, "config_dashboard.tiles", [])
                    // Filter out tiles that doesn't exists anymore,
                    // for dynamic tiles which target has been deleted
                    .filter((tile) => _.has(getters.allTilesByName, tile.name))
            )
        },
        // The tiles currently displayed to the dashboard
        currentTiles(state, getters) {
            return getters.userTilesConfig.map((userTileConfig) => {
                let tile = _.clone(getters.allTilesByName[userTileConfig.name])
                tile.params = _.clone(userTileConfig.params)
                return tile
            })
        },
    },
    actions: {
        addTileToUserTiles({ state, getters, dispatch }, tile) {
            let userTiles = getters.userTilesConfig
            userTiles.push({
                name: tile.name,
                params: tile.params || {},
            })
            dispatch("setUserTiles", userTiles)
        },
        removeTileFromUserTiles({ state, getters, dispatch }, index) {
            let userTiles = getters.userTilesConfig
            userTiles.splice(index, 1)
            dispatch("setUserTiles", userTiles)
        },
        setUserTiles({ state, commit, dispatch }, userTiles) {
            dispatch(
                "users/updateUserField",
                {
                    fieldPath: "config_dashboard.tiles",
                    value: userTiles,
                },
                { root: true },
            )
        },
    },
}
