<!--
This mixin component defines the base behaviour for all icons in Pilot.

Each icon must be loaded as a component by importing the .svg file ( webpack will using svg-loader )
We mainly use the feather-icon library, which have those characteristics
  - A 24-based viewbox : viewBox="0 0 24 24" width="24" height="24"
  - fill="none"
  - stroke="currentColor"

The icons are stroke-based. You can style them with a simple text color, and the "stroke-current" utility is unnecessary.
You can use the "fill-current" utility if needed.
You can change the default size ( 24px ) with the "size" prop ( w-X and h-X classes from tailwind also work, but are less explicit )
Example : <Icon name="IconName" class="text-blue-500" size="20px" />

The svg file MUST keep the original feather name, with kebab-case names converted into snake_case.
The Vue component MUST be named after its usage into Pilot, and NOT after the original feather name.
Example :
Correct : import Wiki from "@svg/book_open.svg"
Incorrect : import BookOpen from "@svg/book_open.svg"
Incorrect : import Wiki from "@svg/wiki.svg"
-->

<template>
<component
    :style="style"
    :is="icon"
    v-bind="attrs"
/>
</template>

<script>
import _ from "lodash"

export default {
    name: "IconMixin",
    props: {
        name: {
            type: String,
            required: true,
        },
        size: {
            type: String,
        },
    },
    data: () => ({
        icons: {},
        defaultIcon: null,
    }),
    computed: {
        icon() {
            return _.get(this.icons, this.name, this.defaultIcon)
        },
        sizeObject() {
            if (this.size) {
                return {
                    width: this.size,
                    height: this.size,
                }
            }
            return {}
        },
        attrs() {
            return this.sizeObject
        },
        style() {
            return this.sizeObject
        },
    },
}
</script>
