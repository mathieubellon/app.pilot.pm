import "../js/index"

import Vue from "vue"
import VueRouter from "vue-router"

import i18n from "@components/i18n"
import { createVuexStore } from "@components/bootstrap"

/***********************
 * Globals
 ************************/

// Mock common requests
function mockCommonRequests() {
    beforeEach(inject(function ($httpBackend) {
        $httpBackend.whenGET("/api/users/").respond([])
        $httpBackend.whenGET("/api/users/me/").respond({})
    }))
}
window.mockCommonRequests = mockCommonRequests

// Mock browser selection getter
document.getSelection = jest.fn(() => {
    return {
        anchorNode: null,
    }
})
// Simulate range object for codemirror init
document.createRange = function () {
    return {
        setEnd: function () {},
        setStart: function () {},
        getClientRects: () => [],
        getBoundingClientRect: () => {
            return {}
        },
    }
}

/***********************
 * Vue.js globals
 ************************/

window.getTestingVueInstance = function (component, store, router) {
    if (store) {
        store = createVuexStore(store)
    }
    if (router) {
        router = new VueRouter(router)
    }
    return new Vue({
        i18n,
        store,
        router,
        render: function (createElement) {
            return createElement(component)
        },
    }).$mount()
}
