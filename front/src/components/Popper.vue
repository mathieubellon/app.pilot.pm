<!--
Warning, each triggerElementName inside a parent component must be unique
You cannot have multiple Popper with `call-to-action` as triggerElementName in the same component.

Example:
<Popper triggerElementName="call-to-action">
    <template #triggerElement>
        <button ref="call-to-action" >
        </button>
    </template>

    <template #content>
    </template>
</Popper>
-->
<template>
<Fragment>
    <slot name="triggerElement" />

    <div
        v-show="isPopperVisible"
        class="popper"
        ref="popper"
    >
        <slot
            v-if="popperShown || !lazyLoading"
            name="content"
        />
    </div>
</Fragment>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import Popper from "popper.js"
import { Fragment } from "vue-fragment"
import BoxEscapingWatcher from "@js/BoxEscapingWatcher"

const DEFAULT_HOVER_DELAY = 200

export default {
    name: "Popper",
    components: {
        Fragment,
    },
    props: {
        triggerType: {
            type: String,
            default: "hover",
            validator: (value) => ["click", "hover"].indexOf(value) > -1,
        },
        visibleArrow: {
            type: Boolean,
            default: true,
        },
        placement: {
            type: String,
            default: "bottom",
        },
        hoverDelay: {
            type: Number,
            default: DEFAULT_HOVER_DELAY,
        },
        preventCloseCallback: Function,
        /**
         * Control if the popper should close when clicking on some element(s) inside the poppers.
         * The value should be A jquery-compatible CSS selector of elements that should close the popper.
         */
        closeOnClickSelector: String,
        boundariesSelector: String,
        /**
         * Control wether the popper content should be loaded only when it's opened the first time.
         */
        lazyLoading: {
            type: Boolean,
            default: true,
        },
        // If multiple Popper in the same parent component, each triggerElementName must be unique
        triggerElementName: {
            type: String,
            required: true,
        },
        /**
         * Allow to move the popper DOM element at the end of #app.
         * This may help with issues, such as sticky + z-index ( ex: RichTextMenuBar )
         */
        appendToBody: {
            type: Boolean,
            default: false,
        },
    },
    data: () => ({
        referenceElm: null,
        popperElm: null,
        popperJS: null,
        isPopperVisible: false,
        popperShown: false,
    }),
    watch: {
        isPopperVisible(value) {
            if (value) {
                this.popperShown = true
                this.$emit("show", this)
                this.updatePopper()
                if (this.popperEscapingWatcher) {
                    this.popperEscapingWatcher.startWatching()
                }
            } else {
                this.$emit("hide", this)
                if (this.popperEscapingWatcher) {
                    this.popperEscapingWatcher.stopWatching()
                }
            }
        },
    },
    methods: {
        togglePopper() {
            this.isPopperVisible = !this.isPopperVisible
        },
        showPopper() {
            this.isPopperVisible = true
        },
        hidePopper() {
            this.isPopperVisible = false
        },
        createPopper() {
            this.popperElm = this.$refs.popper
            this.setupPopperEventHandlers()

            this.$nextTick(() => {
                let popperOptions = {
                    placement: this.placement,
                    computeStyle: {
                        gpuAcceleration: false,
                    },
                }

                if (this.visibleArrow) {
                    this.appendArrow()
                }

                if (this.popperJS && this.popperJS.destroy) {
                    this.popperJS.destroy()
                }

                if (this.boundariesSelector) {
                    const boundariesElement = document.querySelector(this.boundariesSelector)

                    if (boundariesElement) {
                        popperOptions.modifiers = Object.assign({}, popperOptions.modifiers)
                        popperOptions.modifiers.preventOverflow = Object.assign(
                            {},
                            popperOptions.modifiers.preventOverflow,
                        )
                        popperOptions.modifiers.preventOverflow.boundariesElement = boundariesElement
                    }
                }

                popperOptions.onCreate = () => {
                    this.$emit("created", this)
                    this.$nextTick(this.updatePopper)
                }

                this.popperJS = new Popper(this.referenceElm, this.popperElm, popperOptions)
            })
        },
        appendArrow() {
            let $popper = $(this.popperElm)
            if ($popper.find(".popper__arrow").length) {
                // There's already an arrow, no need to create another one
                return
            }
            $popper.append('<div class="popper__arrow" x-arrow=""></div>')
        },
        updatePopper() {
            this.popperJS ? this.popperJS.scheduleUpdate() : this.createPopper()
        },
        onMouseOver() {
            clearTimeout(this._timer)
            this._timer = setTimeout(() => {
                this.isPopperVisible = true
            }, this.hoverDelay)
        },
        onMouseOut() {
            clearTimeout(this._timer)
            this._timer = setTimeout(() => {
                this.isPopperVisible = false
            }, this.hoverDelay)
        },
        onEscape(event) {
            if (this.preventCloseCallback && this.preventCloseCallback(event)) {
                return
            }
            this.isPopperVisible = false
        },
        setupReferenceEventHandlers() {
            switch (this.triggerType) {
                case "click":
                    $(this.referenceElm).on("click", this.togglePopper)
                    break
                case "hover":
                    $(this.referenceElm).on("mouseover", this.onMouseOver)
                    $(this.referenceElm).on("focus", this.onMouseOver)
                    $(this.referenceElm).on("mouseout", this.onMouseOut)
                    $(this.referenceElm).on("blur", this.onMouseOut)
                    break
            }
        },
        setupPopperEventHandlers() {
            switch (this.triggerType) {
                case "click":
                    this.popperEscapingWatcher = new BoxEscapingWatcher(
                        () => [this.$el, this.referenceElm, this.popperElm],
                        this.onEscape,
                    )
                    break
                case "hover":
                    $(this.popperElm).on("mouseover", this.onMouseOver)
                    $(this.popperElm).on("focus", this.onMouseOver)
                    $(this.popperElm).on("mouseout", this.onMouseOut)
                    $(this.popperElm).on("blur", this.onMouseOut)
                    break
            }

            $(this.popperElm).on("click", (event) => {
                if (
                    this.closeOnClickSelector &&
                    $(event.target).closest(this.closeOnClickSelector).length
                ) {
                    this.hidePopper()
                }
                // Update popper position following a click on menu item that may change popper width
                // ( confirmation box for example )
                else {
                    this.updatePopper()
                }
            })
        },
    },
    mounted() {
        if (!this.$slots.triggerElement) {
            return
        }
        let referenceElm = this.$slots.triggerElement[0].context.$refs[this.triggerElementName]
        // Usefull for Poppers in v-for loops
        if (_.isArray(referenceElm)) {
            referenceElm = referenceElm[0]
        }
        this.referenceElm = referenceElm

        this.setupReferenceEventHandlers()

        if (this.appendToBody) {
            $(this.$refs.popper).appendTo("body")
        }
    },
    beforeDestroy() {
        // Remove all listeners on the reference element and the popper
        $(this.referenceElm).off()

        if (this.popperEscapingWatcher) {
            this.popperEscapingWatcher.stopWatching()
        }

        if (this.popperJS) {
            this.popperJS.destroy()
            this.popperJS = null
        }

        let popperElm = this.$refs.popper
        if (popperElm) {
            $(popperElm).off()

            // Elements appended to body must be removed manually, because Vue.js won't do it automatically.
            if (this.appendToBody) {
                popperElm.remove()
            }
        }
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.popper {
    position: absolute;
    width: auto;
    @apply p-3 bg-white rounded;
    // Popper has a z-index of 100. Other elements should position themselves accordingly (generally below)
    z-index: 100;
    box-shadow: rgba(15, 15, 15, 0.05) 0px 0px 0px 1px, rgba(15, 15, 15, 0.1) 0px 3px 6px,
        rgba(15, 15, 15, 0.2) 0px 9px 24px;

    .popper__arrow {
        width: 0;
        height: 0;
        border-style: solid;
        position: absolute;
        margin: 5px;
    }
}

.popper[x-placement^="top"] {
    margin-bottom: 5px;
}

.popper[x-placement^="top"] > .popper__arrow {
    border-width: 5px 5px 0 5px;
    border-color: #fafafa transparent transparent transparent;
    bottom: -5px;
    left: calc(50% - 5px);
    margin-top: 0;
    margin-bottom: 0;
}

.popper[x-placement^="bottom"] {
    margin-top: 5px;
}

.popper[x-placement^="bottom"] > .popper__arrow {
    border-width: 0 5px 5px 5px;
    border-color: transparent transparent #fafafa transparent;
    top: -5px;
    left: calc(50% - 5px);
    margin-top: 0;
    margin-bottom: 0;
}

.popper[x-placement^="right"] {
    margin-left: 5px;
}

.popper[x-placement^="right"] > .popper__arrow {
    border-width: 5px 5px 5px 0;
    border-color: transparent #fafafa transparent transparent;
    left: -5px;
    top: calc(50% - 5px);
    margin-left: 0;
    margin-right: 0;
}

.popper[x-placement^="left"] {
    margin-right: 5px;
}

.popper[x-placement^="left"] > .popper__arrow {
    border-width: 5px 0 5px 5px;
    border-color: transparent transparent transparent #fafafa;
    right: -5px;
    top: calc(50% - 5px);
    margin-left: 0;
    margin-right: 0;
}
</style>
