<template>
<section class="UserMessages">
    <transition-group
        enter-active-class="animated fadeIn"
        leave-active-class="animated fadeOut"
        mode="in-out"
    >
        <div
            v-if="usingIE"
            class="UserMessages__message bg-red-200 text-red-900 font-bold text-lg py-4"
            key="usingIE"
        >
            ⚠ {{ $t("usingIE") }} ⚠
        </div>

        <div
            v-if="isImpersonate"
            class="UserMessages__message impersonate"
            key="impersonate"
        >
            <a href="/impersonate/stop">{{ $t("leaveImpersonate") }}</a>
        </div>

        <div
            v-if="onDemoSite"
            class="UserMessages__message"
            key="demo"
        >
            <span>
                {{ $t("onDemoSite") }}
            </span>

            <div class="flex">
                <form
                    class="mr-4"
                    action=""
                    method="get"
                >
                    <input
                        name="lang"
                        type="hidden"
                        value="en"
                    />
                    <input
                        class="button bg-opacity-25 text-white"
                        type="submit"
                        value="English"
                    />
                </form>

                <form
                    action=""
                    method="get"
                >
                    <input
                        name="lang"
                        type="hidden"
                        value="fr"
                    />
                    <input
                        class="button bg-opacity-25 text-white"
                        type="submit"
                        value="Français"
                    />
                </form>
            </div>
        </div>

        <div
            v-if="lastMessage"
            class="UserMessages__message"
            :class="{ twinkle: lastMessage.twinkle }"
            :key="lastMessage.id"
        >
            <div v-html="lastMessage.content[$i18n.locale]" />
            <button
                class="button is-small is-white"
                @click="dismiss(lastMessage)"
            >
                {{ $t("dismiss") }}
            </button>
        </div>
    </transition-group>
</section>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import browser from "prosemirror-view/src/browser"

export default {
    name: "UserMessages",
    data: () => ({
        isImpersonate: window.pilot.isImpersonate,
        onDemoSite: window.pilot.onDemoSite,
    }),
    computed: {
        ...mapState("users", ["messages"]),
        lastMessage() {
            return this.messages.slice(-1).pop()
        },
        usingIE() {
            return false
            // return browser.ie
        },
    },
    methods: {
        ...mapMutations("users", ["removeMessage"]),
        ...mapActions("users", ["setMessageAsRead"]),
        dismiss(message) {
            this.removeMessage(message)
            if (message.type != "pop" && message.id) {
                this.setMessageAsRead(message)
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                dismiss: "Supprimer",
                leaveImpersonate: "Leave impersonate mode",
                onDemoSite:
                    "Vous êtes sur une version de démonstration, la base de donnée est effacée toutes les heures.",
                usingIE:
                    "Vous utilisez actuellement Internet Explorer. Ce navigateur n'est plus supporté par Pilot car il implique des risques de sécurité, des instabilités et des ralentissements. Tous les autres navigateurs modernes sont supportés.",
            },
            en: {
                dismiss: "Dismiss",
                leaveImpersonate: "Leave impersonate mode",
                onDemoSite: "You are on a demo version, the database is reset every hour.",
                usingIE:
                    "You are currently running Internet Explorer. This browser is not supported anymore by Pilot due to the security risks, instabilities and slowness induced. Every other modern browser is gladly supported.",
            },
        },
    },
}
</script>

<style lang="scss">
.UserMessages__message {
    @apply flex justify-between items-center w-full bg-purple-700 text-purple-100 p-2;

    &.impersonate {
        justify-content: center;
    }

    a {
        @apply text-teal-300 underline;
    }

    @keyframes blinker {
        50% {
            opacity: 0;
        }
    }
    &.twinkle {
        animation: blinker 1s linear infinite;
    }
}
</style>
