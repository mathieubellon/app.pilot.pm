import $ from "jquery"

const WIDTHS = {
    PHONE: 640,
    TABLET: 768,
    DESKTOP: 1024,
    LARGE: 1280,
}

export default {
    namespaced: true,
    state: {
        viewportWidth: null,
    },
    mutations: {
        updateViewportWidth(state) {
            state.viewportWidth = $(window).width()
        },
    },
    getters: {
        viewportPhone: (state) => state.viewportWidth <= WIDTHS.TABLET,
        viewportTablet: (state) =>
            state.viewportWidth > WIDTHS.TABLET && state.viewportWidth <= WIDTHS.DESKTOP,
        viewportDesktop: (state) =>
            state.viewportWidth > WIDTHS.DESKTOP && state.viewportWidth <= WIDTHS.LARGE,
        viewportPhoneToLarge: (state) =>
            state.viewportWidth > WIDTHS.PHONE && state.viewportWidth <= WIDTHS.LARGE,
        viewportLarge: (state) => state.viewportWidth > WIDTHS.LARGE,

        viewportLTEPhone: (state) => state.viewportWidth <= WIDTHS.PHONE,
        viewportLTETablet: (state) => state.viewportWidth <= WIDTHS.TABLET,
        viewportLTEDesktop: (state) => state.viewportWidth <= WIDTHS.DESKTOP,
        viewportLTELarge: (state) => state.viewportWidth <= WIDTHS.LARGE,

        viewportGTEPhone: (state) => state.viewportWidth >= WIDTHS.PHONE,
        viewportGTETablet: (state) => state.viewportWidth >= WIDTHS.TABLET,
        viewportGTEDesktop: (state) => state.viewportWidth >= WIDTHS.DESKTOP,
        viewportGTELarge: (state) => state.viewportWidth >= WIDTHS.LARGE,
    },
    actions: {
        initResponsiveStore({ commit }) {
            commit("updateViewportWidth")
            $(window).on("resize", () => {
                commit("updateViewportWidth")
            })
        },
    },
}
