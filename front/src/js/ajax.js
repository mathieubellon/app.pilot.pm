import _ from "lodash"
import $ from "jquery"
import axios from "axios"
import moment from "moment"

import Emitter from "@js/Emitter"
import { QueryParamSerializer } from "@js/queryString"

const csrfToken = $('input[name="csrfmiddlewaretoken"]').val()
// In seconds
const BUNDLE_CHECK_INTERVAL = 60
let lastBundleCheck = moment()

const $http = axios.create({
    headers: {
        "X-CSRFToken": csrfToken,
    },
    // We need to serialize the params ourselves, because IE11 does not support URLSearchParams
    paramsSerializer(params) {
        return new QueryParamSerializer(params).getQueryString()
    },
})
$http.interceptors.request.use((config) => {
    let now = moment()
    // Check every minutes
    if (now.diff(lastBundleCheck, "seconds") > BUNDLE_CHECK_INTERVAL) {
        config.headers["Bundle-Name"] = window.pilot.bundleName
        lastBundleCheck = now
    }
    return config
})
$http.interceptors.response.use(
    (response) => response,
    (error) => {
        let responseStatus = _.get(error, "response.status")
        let responseDetail = _.get(error, "response.data.detail", "")
        // User has been disconnected, redirect him to the login
        if (responseStatus == 401) {
            window.location = "/login/"
        }
        // CSRF Error, reload the page to get a new CSRF token
        if (responseStatus == 403 && responseDetail.startsWith("CSRF Failed")) {
            window.location.reload()
        }
        // Webpack bundle has been updated, reload the page to get the new version.
        if (responseStatus == 419) {
            window.location.reload()
        }
        return Promise.reject(error)
    },
)

class AxiosEmitter extends Emitter {
    constructor(http) {
        super()

        http.interceptors.response.use(
            (response) => response,
            (error) => this.handleResponseError(error),
        )
    }

    handleResponseError(error) {
        if (error.message == "Network Error") {
            this.emit("networkError", error)
        }
        return Promise.reject(error)
    }
}
let axiosEvents = new AxiosEmitter($http)

// $http in a VueX context, with loading and error handling
function $httpX(config) {
    config = _.defaults(config, {
        showLoading: true,
        handle404: false,
    })

    let name = config.name,
        commit = config.commit,
        showLoading = config.showLoading,
        handle404 = config.handle404

    if (showLoading) commit("loading/startLoading", name, { root: true })

    return $http(config)
        .then((response) => {
            if (showLoading) {
                commit("loading/stopLoadingSuccess", name, { root: true })
            }
            return response
        })
        .catch((error) => {
            if (showLoading) {
                commit("loading/stopLoadingError", { name, error }, { root: true })
            }
            if (handle404 && error.response && error.response.status == 404) {
                commit("setObjectNotFound", true, { root: true })
            } else {
                throw error
            }
        })
}

export { csrfToken, $http, $httpX, axiosEvents }
