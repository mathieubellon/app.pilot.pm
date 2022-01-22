<template>
<input
    :placeholder="placeholder"
    :type="inputType"
    v-model.trim="search"
/>
</template>

<script>
import Fuse from "fuse.js/dist/fuse.common.js"

export default {
    name: "VueFuse",
    data: () => ({
        fuse: null,
        search: "",
        result: [],
    }),
    props: {
        inputType: {
            type: String,
            default: "search",
        },
        defaultAll: {
            type: Boolean,
            default: true,
        },
        placeholder: {
            type: String,
            default: "",
        },
        caseSensitive: {
            type: Boolean,
            default: false,
        },
        includeScore: {
            type: Boolean,
            default: false,
        },
        includeMatches: {
            type: Boolean,
            default: false,
        },
        list: {
            type: Array,
        },
        tokenize: {
            type: Boolean,
            default: true,
        },
        matchAllTokens: {
            type: Boolean,
            default: true,
        },
        findAllMatches: {
            type: Boolean,
            default: false,
        },
        id: {
            type: String,
            default: "",
        },
        shouldSort: {
            type: Boolean,
            default: true,
        },
        threshold: {
            type: Number,
            default: 0.6,
        },
        location: {
            type: Number,
            default: 0,
        },
        distance: {
            type: Number,
            default: 100,
        },
        maxPatternLength: {
            type: Number,
            default: 32,
        },
        minMatchCharLength: {
            type: Number,
            default: 1,
        },
        keys: {
            type: Array,
        },
    },
    computed: {
        options() {
            let options = {
                caseSensitive: this.caseSensitive,
                includeScore: this.includeScore,
                includeMatches: this.includeMatches,
                tokenize: this.tokenize,
                matchAllTokens: this.matchAllTokens,
                findAllMatches: this.findAllMatches,
                shouldSort: this.shouldSort,
                threshold: this.threshold,
                location: this.location,
                distance: this.distance,
                maxPatternLength: this.maxPatternLength,
                minMatchCharLength: this.minMatchCharLength,
                keys: this.keys,
            }
            if (this.id !== "") {
                options.id = this.id
            }
            return options
        },
    },
    watch: {
        search() {
            this.$emit("input", this.search)
            if (this.search === "") {
                if (this.defaultAll) {
                    this.result = this.list
                } else {
                    this.result = []
                }
            } else {
                this.result = this.fuse.search(this.search).map((r) => r.item)
            }
        },
        result() {
            this.$emit("result", this.result)
        },
        // Re-create a Fuse object for each list change ?? It works but is it nice ?
        list() {
            this.initFuse()
            if (this.search) {
                this.result = this.fuse.search(this.search).map((r) => r.item)
            }
        },
    },
    methods: {
        initFuse() {
            this.fuse = new Fuse(this.list, this.options)
            if (this.defaultAll) {
                this.result = this.list
            }
        },
    },
    mounted() {
        this.initFuse()
    },
}
</script>
