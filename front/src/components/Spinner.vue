<template>
<span class="flex items-center justify-center">
    <transition>
        <svg
            class="spinner show-spinner"
            :height="size"
            viewBox="0 0 44 44"
            :width="size"
        >
            <circle
                class="path"
                cx="22"
                cy="22"
                fill="none"
                r="20"
                stroke-linecap="round"
                stroke-width="4"
            ></circle>
        </svg>
    </transition>
</span>
</template>

<script>
export default {
    name: "Spinner",
    props: {
        size: {
            type: String,
            default: "24px",
        },
    },
}
</script>

<style lang="scss">
.spinner {
    transition: opacity 0.15s ease;
    animation: rotator 1.4s linear infinite;
    animation-play-state: paused;
}

.spinner.show-spinner {
    animation-play-state: running;
}

.spinner.v-enter,
.spinner.v-leave-active {
    opacity: 0;
}

.spinner.v-enter-active,
.spinner.v-leave {
    opacity: 1;
}

.spinner .path {
    stroke: #3498db;
    stroke-dasharray: 126;
    stroke-dashoffset: 0;
    transform-origin: center;
    animation: dash 1.4s ease-in-out infinite;
}

@-moz-keyframes rotator {
    0% {
        transform: scale(0.5) rotate(0deg);
    }

    100% {
        transform: scale(0.5) rotate(270deg);
    }
}

@-webkit-keyframes rotator {
    0% {
        transform: scale(0.5) rotate(0deg);
    }

    100% {
        transform: scale(0.5) rotate(270deg);
    }
}

@-o-keyframes rotator {
    0% {
        transform: scale(0.5) rotate(0deg);
    }

    100% {
        transform: scale(0.5) rotate(270deg);
    }
}

@keyframes rotator {
    0% {
        transform: scale(0.5) rotate(0deg);
    }

    100% {
        transform: scale(0.5) rotate(270deg);
    }
}

@-moz-keyframes dash {
    0% {
        stroke-dashoffset: 126;
    }

    50% {
        stroke-dashoffset: 63;
        transform: rotate(135deg);
    }

    100% {
        stroke-dashoffset: 126;
        transform: rotate(450deg);
    }
}

@-webkit-keyframes dash {
    0% {
        stroke-dashoffset: 126;
    }

    50% {
        stroke-dashoffset: 63;
        transform: rotate(135deg);
    }

    100% {
        stroke-dashoffset: 126;
        transform: rotate(450deg);
    }
}

@-o-keyframes dash {
    0% {
        stroke-dashoffset: 126;
    }

    50% {
        stroke-dashoffset: 63;
        transform: rotate(135deg);
    }

    100% {
        stroke-dashoffset: 126;
        transform: rotate(450deg);
    }
}

@keyframes dash {
    0% {
        stroke-dashoffset: 126;
    }

    50% {
        stroke-dashoffset: 63;
        transform: rotate(135deg);
    }

    100% {
        stroke-dashoffset: 126;
        transform: rotate(450deg);
    }
}
</style>
