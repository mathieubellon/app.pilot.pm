<template>
<div
    class="AssetDetailRightElement relative flex items-center justify-center bg-white border-2 border-purple-500 rounded p-2 mr-4 mb-4 h-32 w-full max-w-xs"
>
    <LinkedRemindersModal
        :objectId="assetRight.id"
        :reminders="assetRight.reminders"
        targetType="asset_right_expiry"
    />

    <Popper
        closeOnClickSelector=".willClose"
        triggerElementName="assetRightPopper"
        triggerType="click"
    >
        <template #triggerElement>
            <button
                class="absolute top-0 right-0 mr-2"
                ref="assetRightPopper"
            >
                <Icon name="MenuDotsHorizontal" />
            </button>
        </template>

        <template #content>
            <div>
                <!-- Reminders -->
                <button
                    class="menu-item whitespace-normal willClose"
                    @click.prevent="showRemindersModal(assetRight)"
                >
                    <Icon name="Bell" />

                    <a
                        v-if="assetRight.reminders.length > 0"
                        class="actionlink hover:underline is-gray is-small"
                    >
                        {{
                            $tc("youHaveXReminder", assetRight.reminders.length, [
                                assetRight.reminders.length,
                            ])
                        }}
                    </a>
                    <a
                        v-else="assetRight.deadline"
                        class="actionlink"
                    >
                        {{ $t("addReminder") }}
                    </a>
                </button>

                <!-- Edit -->
                <button
                    class="menu-item willClose"
                    @click="$emit('editAssetRight')"
                >
                    <Icon name="Edit" />
                    {{ $t("edit") }}
                </button>

                <!-- Delete -->
                <MenuItemWithConfirm
                    iconName="Trash"
                    :isRed="true"
                    :label="$t('delete')"
                    @confirmed="deleteAssetRight(assetRight)"
                />
            </div>
        </template>
    </Popper>

    <div class="text-center">
        <strong>{{ assetRight.medium.name }}</strong>
        {{ $t("until") }}
        <strong>{{ assetRight.expiry | dateFormat }}</strong>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import LinkedRemindersModal from "@views/notifications/reminder/LinkedRemindersModal.vue"
import MenuItemWithConfirm from "@components/MenuItemWithConfirm"

export default {
    name: "AssetDetailRightElement",
    mixins: [PilotMixin],
    components: {
        LinkedRemindersModal,
        MenuItemWithConfirm,
    },
    props: {
        assetRight: Object,
    },
    methods: {
        ...mapActions("assetDetail", ["deleteAssetRight"]),
        showRemindersModal(assetRight) {
            this.$modal.show(`linkedReminders-${assetRight.id}`)
        },
    },
    i18n: {
        messages: {
            fr: {
                until: "jusqu'au",
            },
            en: {
                until: "until",
            },
        },
    },
}
</script>

<style lang="scss"></style>
