<template>
<div
    v-if="isInDOM"
    class="OffPanel"
>
    <transition
        enter-active-class="animated fadeIn"
        leave-active-class="animated fadeOut"
        @after-leave="isInDOM = false"
    >
        <div
            v-show="isVisible"
            class="OffPanel__backdrop"
            @click="close"
        ></div>
    </transition>
    <transition
        :enter-active-class="enterAnimation"
        :leave-active-class="leaveAnimation"
    >
        <div
            v-show="isVisible"
            class="OffPanel__container"
            :class="[position, { stretched }]"
            :style="style"
            @keyup.27="close"
        >
            <div
                class="OffPanel__header"
                :class="{ stretched }"
            >
                <div class="OffPanel__header__title">
                    <slot name="offPanelTitle">{{ title }}</slot>
                </div>
                <a
                    class="OffPanel__header__close text-black text-sm font-semibold hover:bg-gray-100 p-2 rounded"
                    @click.prevent="close"
                >
                    {{ $t("close") }}
                </a>
            </div>
            <slot name="offPanelBody"></slot>
        </div>
    </transition>
</div>
</template>

<script>
import $ from "jquery"
import { mapState, mapMutations } from "vuex"
import { keyCodes } from "@js/utils"

const POSITIONS = ["top", "right", "bottom", "left"]
const enterAnimations = {
    top: "slideInDown",
    bottom: "slideInUp",
    left: "slideInLeft",
    right: "slideInRight",
}
const leaveAnimations = {
    top: "slideOutUp",
    bottom: "slideOutDown",
    left: "slideOutLeft",
    right: "slideOutRight",
}

export default {
    name: "OffPanel",
    props: {
        name: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            default: "",
        },
        position: {
            type: String,
            default: "right",
            validator: (value) => {
                return POSITIONS.indexOf(value) !== -1
            },
        },
        width: {
            type: String,
            default: "50%",
        },
        height: {
            type: String,
            default: "50%",
        },
        stretched: {
            type: Boolean,
            default: false,
        },
    },
    data: () => ({
        isInDOM: false,
        isVisible: false,
    }),
    computed: {
        ...mapState("offPanel", ["openedOffPanels"]),
        style() {
            if (this.position == "top" || this.position == "down") return { height: this.height }
            else if (this.position == "right" || this.position == "left")
                return { width: this.width }
        },
        enterAnimation() {
            return "animated " + enterAnimations[this.position]
        },
        leaveAnimation() {
            return "animated " + leaveAnimations[this.position]
        },
        isOpen() {
            return this.openedOffPanels[this.name]
        },
    },
    watch: {
        isOpen() {
            this.$emit(this.isOpen ? "opened" : "closed")

            if (this.isOpen) {
                this.isInDOM = true
            }
            this.$nextTick(() => {
                this.isVisible = this.isOpen
            })
        },
    },
    methods: {
        ...mapMutations("offPanel", ["closeOffPanel"]),
        close() {
            this.closeOffPanel(this.name)
        },
        onKeyDown(e) {
            let key = e.which || e.keyCode
            if (this.isOpen && key === keyCodes.ESCAPE) {
                this.close()
            }
        },
    },
    mounted() {
        $(window).on("keydown", this.onKeyDown)
    },
    beforeDestroy() {
        this.isInDOM = false
        this.isVisible = false
        // When changing route from an Offpanel,
        // the Offpanel component will be immediately removed from the Vue tree,
        // and won't trigger its isInDOM // isVisible watchers on v-if // v-show.
        // We need to explicitely hide the DOM element with jquery, otherwise it will persist on the screen.
        $(this.$el).hide()
        $(window).off("keydown", this.onKeyDown)
    },
}
</script>

<style lang="scss">
@import "~@sass/include_media.scss";
.OffPanel__container {
    @apply flex flex-col p-4;
    background: #fff;
    position: fixed;
    // Below Popper (which is 100)
    // Offpanel has a z-index of 90. Other elements should position themselves accordingly (generally below)
    z-index: 90;
    @include media("<=tablet") {
        width: 100% !important;
    }

    &.stretched {
        @apply p-0;
    }
}

.OffPanel__container.top,
.OffPanel__container.bottom {
    width: 100%;
    right: 0;
    left: 0;
    overflow-x: auto;
}
.OffPanel__container.top {
    top: 0;
}
.OffPanel__container.bottom {
    bottom: 0;
}

.OffPanel__container.right,
.OffPanel__container.left {
    height: 100%;
    top: 0;
    bottom: 0;
    overflow-y: auto;
}
.OffPanel__container.right {
    right: 0;
}
.OffPanel__container.left {
    left: 0;
}

.OffPanel__header {
    @apply flex justify-between items-center flex-shrink-0 mb-4;

    &.stretched {
        @apply p-4 pb-0;
    }
}

.OffPanel__header__title {
    @apply text-lg font-black text-black leading-tight;
}

.OffPanel__body {
    @apply flex-auto;
}

.OffPanel__backdrop {
    background-color: rgba(12, 12, 12, 0.33);
    display: block;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    top: 0;
    // Below OffPanel__container (which is 90)
    z-index: 89;
}
</style>
