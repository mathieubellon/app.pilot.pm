/**
 * The entry point point for the pilot front application
 */

// First thing to do : setup monitoring
import "@js/monitoring.js"

// Polyfill for IE11 compatiblity  ( example of broken behaviour : for...of loop   )
import "core-js/stable"
import "regenerator-runtime/runtime"
import "proxy-polyfill/proxy.min.js"
// Simply importing unorm will polyfill String.prototype.normalize on IE11
import "unorm"

/***********************
 * 3rd parties setup
 ************************/

import _ from "lodash"
// Prevent pollution of the global namespace
_.noConflict()

/***********************
 * Pilot assets setup
 ************************/

/** Localization */
import "@js/localize.js"

/** Sass */
import "@sass/index.scss"

/** Favicon */
import "@/assets/favicon.ico"

/***********************
 * Vue setup
 ************************/

import Vue from "vue"
import VueRouter from "vue-router"
import Vuelidate from "vuelidate"
import Vuex from "vuex"
import VTooltip from "v-tooltip"
import VModal from "vue-js-modal"

Vue.config.devtools = true
Vue.config.productionTip = true

Vue.use(Vuex)
Vue.use(VueRouter)
Vue.use(Vuelidate)

Vue.use(VTooltip)
Vue.use(VModal)

// Merge i18n message dict during component .extends()  (example: Mixins)
let strategies = Vue.config.optionMergeStrategies
strategies.i18n = function (parentVal, childVal) {
    if (!parentVal) return childVal
    if (!childVal) return parentVal
    _.defaultsDeep(childVal.messages, parentVal.messages)
    return childVal
}

/***********************
 * HMR
 ************************/

if (module.hot) {
    module.hot.accept()
}

/***********************
 * Application bootstraping
 ************************/

import $ from "jquery"
import { sync } from "vuex-router-sync"
import { installVueFilters } from "@js/filters"
import urls from "@js/urls"
import { $httpX, axiosEvents } from "@js/ajax"
import { EVENTS } from "@js/events"
import i18n from "@js/i18n"
import realtime from "@js/realtime"
import { QueryParamSerializer } from "@js/queryString"

import BulkActionStore from "@/store/modules/BulkActionStore"
import ChoicesStore from "@/store/modules/ChoicesStore"
import FavoritesStore from "@/store/modules/FavoritesStore"
import LabelStore from "@/store/modules/LabelStore"
import ListConfigStore from "@/store/modules/ListConfigStore"
import LoadingStore from "@/store/modules/LoadingStore"
import MyTasksPanelStore from "@/store/modules/MyTasksPanelStore.js"
import NotificationSettingsStore from "@/store/modules/NotificationSettingsStore"
import NotificationStore from "@/store/modules/NotificationStore"
import OffPanelStore from "@/store/modules/OffPanelStore"
import ResponsiveStore from "@/store/modules/ResponsiveStore"
import SavedFilterStore from "@/store/modules/SavedFilterStore.js"
import SharingsStore from "@/store/modules/SharingsStore.js"
import UsageLimitsStore from "@/store/modules/UsageLimitsStore"
import UserStore from "@/store/modules/UserStore"

import UserMessages from "@views/messaging/UserMessages"

const vueApps = []
const scrollPosHistory = {}
let mainApp = null
let router = null
let initialDataPromise = null

function registerVueApp({
    element,
    component = null,
    router = null,
    store = {},
    routerViewAsRoot = false,
}) {
    vueApps.push({ element, component, router, store, routerViewAsRoot })
}

let bootstrapped = false
function bootstrapVue() {
    if (bootstrapped) {
        return
    }
    bootstrapped = true

    $(() => {
        let mountedApp
        for (let vueApp of vueApps) {
            mountedApp = mountVueApp(vueApp)
            if (mountedApp) {
                mainApp = mountedApp

                axiosEvents.on("networkError", (error) => {
                    mountedApp.$store.commit(
                        "users/popMessage",
                        mountedApp.$t("userMessages.networkError"),
                    )
                })

                break
            }
        }
    })
}

function mountVueApp(vueApp) {
    if (!$(vueApp.element).length) {
        return null
    }

    // Setup filters
    installVueFilters()

    let store = createVuexStore(vueApp.store)
    // Enable this if you need to track vuex actions
    /* store.subscribeAction((action, state) => {
        console.log(action.type)
        console.log(action.payload)
    }) */
    if (vueApp.router) {
        router = new VueRouter(vueApp.router)
        router.beforeEach((to, from, next) => {
            if (store) {
                store.commit("setObjectNotFound", false)
            }
            // Prevent memory leaks
            realtime.removeAllMessageHandlers()
            next()
        })
        router.afterEach((to, from) => {
            rememberScrollPos(from)
            setTimeout(() => {
                applyScrollPos(to)
            }, 1)
            if (store) {
                store.commit("offPanel/closeAllOffPanels")
            }
        })
        router.afterEach((to) => {
            let routeTitle = _.get(to, "matched.0.meta.title")
            if (routeTitle) {
                document.title = "Pilot - " + routeTitle
            }
        })

        sync(store, router)
    } else {
        router = new VueRouter({})
    }

    // Init the message mini-app
    new Vue({
        functional: true,
        el: "#user-messages",
        store,
        i18n,
        render: (createElement) => createElement(UserMessages),
    })

    // Init the main app
    return new Vue({
        functional: true,
        el: vueApp.element,
        store,
        router,
        i18n,
        render(createElement) {
            return createElement(
                vueApp.routerViewAsRoot ? Vue.component("router-view") : vueApp.component,
            )
        },
    })
}

function createVuexStore(store = {}) {
    let defaultModules = {
        bulk: BulkActionStore,
        choices: ChoicesStore,
        favorites: FavoritesStore,
        labels: LabelStore,
        listConfig: ListConfigStore,
        loading: LoadingStore,
        notificationSettings: NotificationSettingsStore,
        notifications: NotificationStore,
        offPanel: OffPanelStore,
        responsive: ResponsiveStore,
        savedFilter: SavedFilterStore,
        sharings: SharingsStore,
        tasks: MyTasksPanelStore,
        usageLimits: UsageLimitsStore,
        users: UserStore,
    }

    // Clone the top-level variables, to prevent memory leak incurred by a top-level reactive object.
    let defaultState = {
        contentTypes: _.cloneDeep(window.pilot.contentTypes),
        currentDesk: _.cloneDeep(window.pilot.desk),
    }

    if (!store.modules) {
        store.modules = {}
    }
    if (!store.state) {
        store.state = {}
    }
    if (!store.actions) {
        store.actions = {}
    }

    _.defaults(store.modules, defaultModules)
    _.defaults(store.state, defaultState)

    // Ensure that events always have a corresponding listener, else vuex will complain with an error.
    for (let eventName in EVENTS) {
        store.actions[EVENTS[eventName]] = () => {}
    }

    store = new Vuex.Store(store)

    // At startup, immediately load initial data
    fetchInitialData(store)

    store.dispatch("responsive/initResponsiveStore")
    return store
}

function fetchInitialData(store) {
    // Bail out if the user is not authenticated
    if (!window.pilot.user.id) {
        return
    }

    initialDataPromise = $httpX({
        commit: store.commit,
        name: "fetchInitialData",
        method: "GET",
        url: urls.initialData,
    }).then((response) => {
        let initialData = response.data

        if (store.state.favorites) {
            store.commit("favorites/setFavorites", initialData.favorites)
        }
        if (store.state.users) {
            store.commit("users/setUserMe", initialData.user_me)
        }
        if (store.state.taskGroup) {
            store.commit("taskGroup/setTaskGroups", initialData.task_groups)
        }
        if (store.state.itemTypes) {
            store.commit("itemTypes/setItemTypes", initialData.item_types)
        }
        if (store.state.usersAdmin) {
            store.commit("usersAdmin/setTeams", initialData.teams)
        }
        if (store.state.workflow) {
            store.commit("workflow/setWorkflowStates", initialData.workflow_states)
        }

        for (let choicesName in initialData.choices) {
            store.commit("choices/setChoices", {
                choices: initialData.choices[choicesName],
                choicesName: choicesName,
            })
        }

        return initialData
    })
}

function rememberScrollPos(route) {
    if (!$("#app-body").length) {
        return
    }
    let key = route.path + new QueryParamSerializer(route.query).getQueryString()
    scrollPosHistory[key] = $("#app-body").scrollTop()
}
export function applyScrollPos(route) {
    let key = route.path + new QueryParamSerializer(route.query).getQueryString()
    let scrollPos = scrollPosHistory[key]
    if (!scrollPos || !$("#app-body").length) {
        return
    }
    $("#app-body").scrollTop(scrollPos)
}

export {
    registerVueApp,
    bootstrapVue,
    mountVueApp,
    createVuexStore,
    mainApp,
    router,
    initialDataPromise,
}
