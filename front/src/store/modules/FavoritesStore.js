import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

export default {
    namespaced: true,
    state: {
        favorites: [],
    },
    mutations: {
        setFavorites(state, favorites) {
            state.favorites = favorites
        },
        appendToFavorites(state, favorite) {
            state.favorites = state.favorites.concat(favorite)
        },
        removeFavorite(state, favorite) {
            state.favorites = state.favorites.filter((f) => f.id != favorite.id)
        },
    },
    actions: {
        fetchFavorites({ commit }) {
            return $httpX({
                commit,
                name: "fetchFavorites",
                method: "GET",
                url: urls.favorites,
            }).then((response) => {
                commit("setFavorites", response.data)
            })
        },
        createFavorite({ commit }, favorite) {
            return $httpX({
                commit,
                name: "toggleFavorite",
                method: "POST",
                url: urls.favorites,
                data: favorite,
            }).then((response) => {
                commit("appendToFavorites", response.data)
            })
        },
        deleteFavorite({ state, commit }, favorite) {
            $httpX({
                name: "toggleFavorite",
                commit,
                url: urls.favorites.format({ id: favorite.id }),
                method: "DELETE",
            }).then((response) => {
                // Remove the favorite from the list
                commit("removeFavorite", favorite)
            })
        },
    },
}
