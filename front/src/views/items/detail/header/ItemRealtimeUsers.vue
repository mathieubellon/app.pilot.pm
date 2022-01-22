<template>
<Popper
    triggerElementName="PopperRef"
    triggerType="hover"
    :visibleArrow="false"
>
    <template #triggerElement>
        <div
            class="flex content-center items-center flex-shrink-0 cursor-pointer"
            ref="PopperRef"
        >
            <div
                v-if="isPageUnloading"
                class="text-sm"
            >
                {{ $t("unloading") }}
            </div>
            <template v-else-if="realtime.state == realtime.STATES.CLOSED">
                <span
                    class="inline-block h-6 w-6 rounded-full overflow-hidden text-white shadow-solid bg-gray-100"
                >
                    <svg
                        class="h-full w-full text-gray-300"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z"
                        />
                    </svg>
                </span>
                <span
                    class="inline-block h-6 w-6 -ml-2 text-white shadow-solid rounded-full overflow-hidden bg-gray-100"
                >
                    <svg
                        class="h-full w-full text-gray-300"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z"
                        />
                    </svg>
                </span>
            </template>
            <template v-else>
                <div class="flex overflow-hidden">
                    <template v-for="(user, index) in realtimeUsers">
                        <span
                            v-if="!user.avatar"
                            class="inline-flex items-center justify-center h-6 w-6 rounded-full bg-gray-400 text-white shadow-solid"
                            :class="{ '-ml-2': index > 0 }"
                        >
                            <span class="text-sm font-medium leading-none text-white">
                                {{ user.username | firstLetter }}
                            </span>
                        </span>
                        <UserAvatar
                            v-else
                            class="inline-block h-6 w-6 rounded-full text-white shadow-solid"
                            :class="{ '-ml-2': index > 0 }"
                            size="18px"
                            :user="user"
                        />
                    </template>
                    <!--                    <img class="-ml-2 inline-block h-8 w-8 rounded-full text-white shadow-solid" src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" alt="" />-->
                    <!--                    <img class="-ml-2 inline-block h-8 w-8 rounded-full text-white shadow-solid" src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2.25&w=256&h=256&q=80" alt="" />-->
                </div>
            </template>
        </div>
    </template>

    <template #content>
        <span class="flex flex-col max-w-xs">
            <span
                v-if="realtime.state == realtime.STATES.CLOSED"
                class="leading-tight"
            >
                {{ $t("degradedMode") }}
            </span>
            <div class="flex flex-col" v-else>
                <span class="font-bold text-sm mb-4">{{ $t("online") }}</span>
                <span
                    v-for="user in realtimeUsers"
                    class="rounded-full mb-2"
                >
                    <div
                        v-if="!user.avatar"
                        class="flex items-center font-medium my-1"
                        :style="{ color: user.color }"
                    >
                        <span
                            class="flex items-center justify-center h-6 w-6 rounded-full bg-gray-400 text-white shadow-solid"
                        >
                            <span class="text-sm font-medium leading-none text-white">
                                {{ user.username | firstLetter }}
                            </span>
                        </span>
                        {{ user.username }}
                    </div>
                    <UserDisplay
                        v-else
                        avatarSize="24px"
                        :color="user.color"
                        :user="user"
                        :withAvatar="true"
                        :withUsername="true"
                    />
                </span>
            </div>
        </span>
    </template>
</Popper>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import realtime from "@js/realtime"

import PilotMixin from "@components/PilotMixin"

export default {
    name: "ItemRealtimeUsers",
    mixins: [PilotMixin],
    data: () => ({
        isPageUnloading: false,
        realtime,
    }),
    computed: {
        ...mapState("itemContentForm", ["realtimeUsers"]),
    },
    i18n: {
        messages: {
            fr: {
                degradedMode:
                    "Vous êtes en mode dégradé, les autres utilisateurs connectés ne sont pas visibles mais vous pouvez continuer à éditer le contenu - rechargez la page",
                nowReading: "Présents sur la page",
                unloading: "Déconnexion",
                usersConnected: "Actuellement connecté.e.s à cette page",
            },
            en: {
                degradedMode:
                    "You are in downgraded mode, other logged-in users are not visible but you can continue to edit the content - reload the page",
                nowReading: "Present on the page",
                unloading: "Disconnecting",
                usersConnected: "Currently reading",
            },
        },
    },
}
</script>
