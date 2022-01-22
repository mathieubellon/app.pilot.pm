import Vue from "vue"
import _ from "lodash"
import * as Sentry from "@sentry/browser"
import { Integrations as ApmIntegrations } from "@sentry/apm"
import { Vue as VueIntegration } from "@sentry/integrations"

// Monitoring API
let $monitoring = {
    captureException: (error, extraData = {}) => {},
    captureMessage: (message, extraData = {}) => {},
}

/** Setup monitoring **/
if (window.pilot.sentryEnabled) {
    Sentry.init({
        dsn: window.pilot.djangoSettings.SENTRY_FRONTEND_DSN,
        release: window.pilot.sentryRelease,
        integrations: [
            new ApmIntegrations.Tracing(),
            new VueIntegration({
                Vue,
                tracing: true,
            }),
        ],
        tracesSampleRate: 0.2,
    })
    Sentry.configureScope((scope) => {
        scope.setUser(window.pilot.user)
    })

    let defaultData = {}
    if (window.pilot) {
        if (window.pilot.desk.id) {
            defaultData.deskId = window.pilot.desk.id
            defaultData.deskName = window.pilot.desk.name
        }
    }

    $monitoring.captureException = function (error, extraData = {}) {
        extraData = _.defaults({}, defaultData, error.extraData, extraData)

        Sentry.withScope((scope) => {
            for (let key in extraData) scope.setExtra(key, extraData[key])
            Sentry.captureException(error)
        })
    }
    $monitoring.captureMessage = function (message, extraData = {}) {
        extraData = _.defaults({}, defaultData, extraData)

        Sentry.withScope((scope) => {
            for (let key in extraData) scope.setExtra(key, extraData[key])
            Sentry.captureMessage(message)
        })
    }

    Vue.config.errorHandler = function (error, vm, info) {
        $monitoring.captureException(error, info)
    }
}
// If sentry is not loaded, make a dummy API
else {
    $monitoring.captureException = (error, extraData = {}) => {
        console.error(error)
        extraData = _.defaults({}, error.extraData, extraData)
        console.error("extraData", JSON.stringify(extraData))
    }
    $monitoring.captureMessage = $monitoring.captureException
}

export default $monitoring
