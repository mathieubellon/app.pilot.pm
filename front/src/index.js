import { bootstrapVue, registerVueApp, mountVueApp } from "@js/bootstrap"

import $ from "jquery"

import MainAppStore from "@/store/MainAppStore"
import MainAppRouter from "@/router/MainAppRouter"
import MainApp from "@views/MainApp"
import MainMenu from "@components/layout/MainMenu"

/**
 * Main App for Pilot
 */
registerVueApp({
    element: "#vue-main-app",
    router: MainAppRouter,
    store: MainAppStore,
    component: MainApp,
})

// Needed on some statics pages ( message.html, 404.html... )
$(() => {
    mountVueApp({
        element: "#vue-mainmenu",
        component: MainMenu,
    })
})

/**
 * Authenticated users may also access any public app.
 * We import them here.
 */
require("./indexPublic")

bootstrapVue()
