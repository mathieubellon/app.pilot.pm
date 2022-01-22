import { bootstrapVue, registerVueApp } from "@js/bootstrap"

import PublicSharingStore from "@/store/PublicSharingStore"

import UserAuthRouter from "@/router/UserAuthRouter"
import PublicSharingRouter from "@/router/PublicSharingRouter"

import PublicSharingApp from "@views/PublicSharingApp"
import NotificationSettingsApp from "@views/NotificationSettingsApp"

/**
 * Authentication App ( authentication, registration, password lost... )
 */
registerVueApp({
    element: "#vue-user-auth",
    router: UserAuthRouter,
    routerViewAsRoot: true,
})

/**
 * Public Sharing App
 */
registerVueApp({
    element: "#vue-sharing",
    router: PublicSharingRouter,
    store: PublicSharingStore,
    component: PublicSharingApp,
})

/**
 * Notifications Settings App ( manage your email notifications without login in )
 */
registerVueApp({
    element: "#vue-notifications-settings",
    component: NotificationSettingsApp,
})

bootstrapVue()
