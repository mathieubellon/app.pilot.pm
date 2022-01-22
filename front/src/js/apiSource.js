import _ from "lodash"
import Vue from "vue"
import { router } from "@js/bootstrap"
import urls from "@js/urls"
import { QueryParamSerializer } from "@js/queryString"

const LIST_OMIT_FILTERS = ["page", "order_by"]
const CALENDAR_OMIT_FILTERS = ["page", "order_by", "start", "end"]

/*********************
 * Api Source components
 ********************/

let ListApiSource = Vue.extend({
    data: () => ({
        getEndpoint: null,
        isCalendar: false,
        omitFilters: null,
    }),
    computed: {
        query() {
            throw Error("Not Implemented")
        },

        endpoint() {
            return this.getEndpoint(this)
        },

        ordering() {
            return _.isArray(this.query.order_by) ? this.query.order_by[0] : this.query.order_by
        },

        page() {
            return _.isArray(this.query.page) ? this.query.order_by[0] : this.query.page
        },

        start() {
            return _.isArray(this.query.start) ? this.query.start[0] : this.query.start
        },

        end() {
            return _.isArray(this.query.end) ? this.query.end[0] : this.query.end
        },

        filters() {
            if (!this.omitFilters) {
                this.omitFilters = this.isCalendar ? CALENDAR_OMIT_FILTERS : LIST_OMIT_FILTERS
            }
            return _.omit(this.query, this.omitFilters)
        },

        filtersCount() {
            return _.keys(this.filters).length
        },

        hasFilter() {
            return this.filtersCount > 0
        },

        queryParamSerializer() {
            return new QueryParamSerializer(this.query)
        },

        queryString() {
            return this.queryParamSerializer.getQueryString()
        },

        url() {
            if (!this.endpoint) {
                return null
            }

            let url = this.endpoint
            if (this.queryString) {
                url += "?" + this.queryString
            }
            return url
        },
    },
    methods: {
        setQuery(query) {
            throw Error("Not Implemented")
        },

        setQueryString(queryString) {
            let serializer = new QueryParamSerializer(queryString)
            this.setQuery(serializer.params)
        },

        setPage(page) {
            this.setQuery({ ...this.query, page })
        },

        setOrdering(ordering) {
            this.setQuery({ ...this.query, order_by: ordering })
        },

        setFilterItems(filterItems) {
            let queryParamSerializer = new QueryParamSerializer()
            queryParamSerializer.addFromBigFilter(filterItems)
            // Reset the page to 1 when we're changing the filters,
            // to avoid landing too far in the pagination
            queryParamSerializer.removeParam("page")
            if (this.ordering) {
                queryParamSerializer.setParam("order_by", this.ordering)
            }
            if (this.query.folder) {
                queryParamSerializer.setParam("folder", this.query.folder)
            }
            if (this.isCalendar) {
                if (this.start) {
                    queryParamSerializer.setParam("start", this.start)
                }
                if (this.end) {
                    queryParamSerializer.setParam("end", this.end)
                }
            }
            this.setQuery(queryParamSerializer.params)
        },

        setFilter(name, value) {
            let serializer = new QueryParamSerializer(this.query)
            serializer.setParam(name, value)
            this.setQuery(serializer.params)
        },

        removeFilter(name) {
            let serializer = new QueryParamSerializer(this.query)
            serializer.removeParam(name)
            this.setQuery(serializer.params)
        },
    },
})

let InMemoryListApiSource = Vue.extend({
    mixins: [ListApiSource],
    data: () => ({
        queryStore: {},
    }),
    computed: {
        query() {
            return this.queryStore
        },
    },
    methods: {
        setQuery(query) {
            this.queryStore = query
        },
    },
})

let RouteListApiSource = Vue.extend({
    mixins: [ListApiSource],
    computed: {
        query() {
            return this.$route.query
        },
    },
    methods: {
        setQuery(query) {
            this.$router.replace({ query })
        },
    },
})

/*********************
 * Api Source constructors
 ********************/

function getRouteApiSource(config) {
    return new Vue({
        router,
        mixins: [RouteListApiSource],
        data: config,
    })
}

export function getProjectApiSource() {
    function getProjectApiEndpoint(vm) {
        switch (vm.$route.name) {
            case "projectList-idea":
                return urls.projectsIdea
            case "projectList-closed":
                return urls.projectsClosed
            default:
                return urls.projectsActive
        }
    }

    return getRouteApiSource({
        getEndpoint: getProjectApiEndpoint,
    })
}

export function getItemApiSource() {
    function getItemApiEndpoint(vm) {
        switch (vm.$route.name) {
            case "itemList-trash":
                return urls.itemsTrashList
            default:
                return urls.items
        }
    }

    return getRouteApiSource({
        getEndpoint: getItemApiEndpoint,
    })
}

export function getItemsChoicesApiSource() {
    return getRouteApiSource({
        getEndpoint: () => urls.itemsChoices,
    })
}

export function getItemsForProjectApiSource(projectId) {
    return getRouteApiSource({
        getEndpoint: () => urls.itemsForProject.format({ projectId }),
    })
}

export function getItemsForChannelApiSource(channelId) {
    return getRouteApiSource({
        getEndpoint: () => urls.itemsForChannel.format({ channelId }),
    })
}

export function getSharedItemApiSource(token) {
    return getRouteApiSource({
        getEndpoint: () => urls.itemsShared.format({ token }),
    })
}

export function getItemCalendarApiSource() {
    return getRouteApiSource({
        getEndpoint: () => urls.itemsForCalendar,
        isCalendar: true,
    })
}

export function getProjectCalendarApiSource() {
    return getRouteApiSource({
        getEndpoint: () => urls.projectsForCalendar,
        isCalendar: true,
    })
}

export function getSharedItemCalendarApiSource(token) {
    return getRouteApiSource({
        getEndpoint: () => urls.itemsSharedForCalendar.format({ token }),
        isCalendar: true,
    })
}

export function getSharedProjectCalendarApiSource(token) {
    return getRouteApiSource({
        getEndpoint: () => urls.projectsSharedForCalendar.format({ token }),
        isCalendar: true,
    })
}

export function getChannelApiSource() {
    function getChannelApiEndpoint(vm) {
        switch (vm.$route.name) {
            case "channelList-closed":
                return urls.channelsClosed
            default:
                return urls.channelsActive
        }
    }

    return getRouteApiSource({
        getEndpoint: getChannelApiEndpoint,
    })
}

export function getAssetApiSource() {
    return getRouteApiSource({
        getEndpoint: () => urls.assetsLibrary,
    })
}

export function getSharingsApiSource() {
    return getRouteApiSource({
        getEndpoint: () => urls.sharingsPaginated,
    })
}

export function getInMemoryApiSource(endpoint) {
    return new Vue({
        router,
        mixins: [InMemoryListApiSource],
        data: {
            getEndpoint: () => endpoint,
        },
    })
}
