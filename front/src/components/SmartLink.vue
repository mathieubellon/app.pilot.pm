<template>
<component
    :href="to"
    :is="component"
    :to="to"
>
    <slot />
</component>
</template>

<script>
/**
 * SmartLink is a component that chose between renderink a link either as :
 *  - a <router-link> component if there's a matching route in the current router
 *  - a <a> element if there's no matching route
 */

// A simple VUe component that simply render an <a> element and its default slot.
let aComponent = {
    render(createElement) {
        return createElement("a", {}, this.$slots.default)
    },
}

export default {
    name: "SmartLink",
    props: {
        to: [String, Object],
    },
    computed: {
        isRoutable() {
            if (!this.$router || !this.to) return false

            // Vue-router complains in the console when we try to resolve an non-existing target.
            // We silence those warnings by tinkering with console.warn
            let oldWarn = console.warn
            console.warn = function () {}
            let matched = this.$router.getMatchedComponents(this.to)
            console.warn = oldWarn
            return matched.length > 0 && matched[0].name != "NotFoundComponent"
        },
        component() {
            return this.isRoutable ? "router-link" : aComponent
        },
    },
}
</script>
