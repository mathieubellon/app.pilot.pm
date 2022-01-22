<template>
<div
    v-show="show"
    class="RichTextTooltip popper"
    :class="{ opened }"
>
    <div class="popper__content"><slot /></div>
    <div
        class="popper__arrow"
        x-arrow=""
    ></div>
</div>
</template>

<script>
import $ from "jquery"
import Popper from "popper.js"
import PopperUtils from "popper.js/dist/esm/popper-utils.js"
import BoxEscapingWatcher from "@js/BoxEscapingWatcher"

export default {
    name: "RichTextTooltip",
    props: {
        direction: {
            type: String,
            default: "top",
        },
        show: Boolean,
        positionBoundingRect: {
            default: {},
        },
    },
    data: () => ({
        opened: false,
    }),
    watch: {
        show() {
            this.show ? this.open() : this.close()
        },
        positionBoundingRect: {
            deep: true,
            handler() {
                this.schedulePopperUpdate()
            },
        },
    },
    methods: {
        open() {
            // Close the tooltip when clicking outside it
            this.tooltipEscapingWatcher.startWatching()

            // Wait *after* the popper has been opened before triggering the movement transition effect
            setTimeout(() => {
                this.opened = true
            }, 50)
        },

        close() {
            this.opened = false

            // Wait 50ms and ensure the tooltip is still closed before actuyally closing it.
            // This will avoid flickering when the user click on another link / image.
            setTimeout(() => {
                if (!this.opened) {
                    this.tooltipEscapingWatcher.stopWatching()
                }
            }, 50)
        },

        schedulePopperUpdate() {
            if (this.popperJS && this.show) {
                this.popperJS.scheduleUpdate()
            }
        },
    },
    mounted() {
        // Get the boundaries element before moving the popper element
        let boundariesElement = PopperUtils.getScrollParent(this.$el)

        // Move the popper to the end of the app to make positioning easier
        $(this.$el).appendTo("body")

        // Setup the popperJs where the dropdown will show up
        let popperReference = {
            getBoundingClientRect: () => this.positionBoundingRect,
            clientWidth: () => this.positionBoundingRect.width,
            clientHeight: () => this.positionBoundingRect.height,
        }

        this.popperJS = new Popper(popperReference, this.$el, {
            placement: this.direction,
            modifiers: {
                preventOverflow: {
                    boundariesElement: boundariesElement,
                    priority: ["left", "top"],
                },
                flip: {
                    boundariesElement: boundariesElement,
                    behavior: ["top", "bottom", "left", "right"],
                },
            },
        })

        this.tooltipEscapingWatcher = new BoxEscapingWatcher(
            () => [this.$el],
            () => this.$emit("escape"),
        )
    },
    beforeDestroy() {
        if (this.tooltipEscapingWatcher) {
            this.tooltipEscapingWatcher.stopWatching()
        }

        if (this.popperJS) {
            this.popperJS.destroy()
        }

        // Elements appended to body must be removed manually, because Vue.js won't do it automatically.
        if (this.$el) {
            this.$el.remove()
        }
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
@import "~@sass/mixins.scss";

.RichTextTooltip {
    box-sizing: border-box;
    -moz-box-sizing: border-box;

    border-radius: 5px;
    padding: 3px 7px;
    margin: 0;
    background: $greyblue500;
    border: 1px solid $greyblue500;
    color: $grey500;

    //z-index: 11;

    &[x-placement^="top"] > .popper__arrow {
        border-color: $greyblue500 transparent transparent transparent;
    }
    &[x-placement^="bottom"] > .popper__arrow {
        border-color: transparent transparent $greyblue500 transparent;
    }
    &[x-placement^="right"] > .popper__arrow {
        border-color: transparent $greyblue500 transparent transparent;
    }
    &[x-placement^="left"] > .popper__arrow {
        border-color: transparent transparent transparent $greyblue500;
    }

    &[x-out-of-boundaries] {
        opacity: 0;
    }

    input::placeholder,
    textarea::placeholder {
        color: $grey600;
    }

    a {
        color: $blue-light;
    }
}

// Wait *after* the popper has been opened before triggering the movement transition effect
.RichTextTooltip.opened {
    @include transition(transform 0.25s ease-out, opacity 0.2s);
}

.RichTextTooltip input[type="text"],
.RichTextTooltip textarea {
    background: #eee;
    border: none;
    outline: none;
}

.RichTextTooltip input[type="text"] {
    padding: 0 4px;
}
</style>
