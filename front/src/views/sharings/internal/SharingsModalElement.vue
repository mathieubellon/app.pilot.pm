<template>
<div class="SharingsModalElement simple-panel m-0 mt-1 px-2 py-1">
    <div class="flex items-center justify-between">
        <div class="flex items-center">
            <span
                class="rounded-full bg-teal-200 mr-2 font-bold text-lg h-8 w-8 flex items-center justify-center"
            >
                {{ sharing.email[0].toUpperCase() }}
            </span>

            <div class="flex flex-col">
                <span class="mr-2">{{ sharing.email }}</span>
                <span class="text-xs text-gray-500">
                    {{ sharing.created_at | dateTimeFormat }}
                </span>
            </div>
        </div>

        <Popper
            triggerElementName="SharingOptionsRef"
            triggerType="click"
        >
            <template #triggerElement>
                <button ref="SharingOptionsRef">
                    <Icon name="MenuDotsVertical" />
                </button>
            </template>

            <template #content>
                <div
                    class="flex flex-col"
                    style="width: 250px"
                >
                    <div class="mb-2 px-2 py-1">
                        <template v-if="sharing.password">
                            {{ $t("password") }} :
                            <span class="font-bold">{{ sharing.password }}</span>
                        </template>
                        <template v-else>
                            {{ $t("noPassword") }}
                        </template>
                    </div>

                    <input
                        class="SharingElement__link cursor-pointer mb-2 px-2 py-1"
                        readonly
                        type="text"
                        :value="sharing.public_url"
                    />

                    <a
                        class="menu-item"
                        :href="sharing.public_url"
                        target="_blank"
                    >
                        <Icon name="ExternalLink" />
                        {{ $t("seeSharing") }}
                    </a>

                    <MenuItemWithConfirm
                        :confirmMessage="$t('thisActionCannotBeUndone')"
                        iconName="Trash"
                        :isRed="true"
                        :label="$t('deactivateSharing')"
                        :loadingName="`deactivateSharing-${sharing.token}`"
                        @confirmed="deactivateSharing(sharing)"
                    />
                </div>
            </template>
        </Popper>
    </div>

    <SharingsModalFeedbackElement
        v-for="feedback in sharing.feedbacks"
        :feedback="feedback"
        :key="feedback.id"
        :sharing="sharing"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import MenuItemWithConfirm from "@components/MenuItemWithConfirm"
import SharingsModalFeedbackElement from "./SharingsModalFeedbackElement"

export default {
    name: "SharingsModalElement",
    mixins: [PilotMixin],
    components: {
        MenuItemWithConfirm,
        SharingsModalFeedbackElement,
    },
    props: {
        sharing: Object,
    },
    methods: {
        ...mapActions("sharings", ["deactivateSharing"]),
    },
    i18n: {
        messages: {
            fr: {
                deactivateSharing: "Désactiver le partage",
                noPassword: "Pas de mot de passe",
                seeSharing: "Voir le partage",
            },
            en: {
                deactivateSharing: "Deactivate the sharing",
                noPassword: "No password",
                seeSharing: "See the sharing",
            },
        },
    },
}
</script>

<style lang="scss"></style>
