<template>
<div class="ItemDetailOptions">
    <!--Sharing Modal-->
    <button
        v-if="!item.in_trash"
        class="menu-item is-teal"
        @click="$modal.show('sharings-item')"
    >
        <Icon name="Share" />
        {{ $tc("sharingsButton", sharings.length, [sharings.length]) }}
    </button>

    <!--Translation tab-->
    <button
        v-if="currentDesk.itemLanguagesEnabled"
        class="menu-item"
        @click="openedDrawer != 'translations' ? openDrawer('translations') : closePanel()"
    >
        <Icon name="Language" />
        <span>{{ $t("translations") }}</span>
    </button>

    <!-- Frozen item -->
    <button
        v-if="!item.frozen"
        class="menu-item"
        @click="$modal.show('freezeItem')"
    >
        <Icon name="LockOpen" />
        {{ $t("freeze") }}
    </button>

    <MenuItemWithConfirm
        v-else
        :confirmMessage="$t('unfreezeConfirmMessage')"
        iconName="LockClosed"
        :isYellow="true"
        :label="$t('unfreeze')"
        :loading="fieldsCurrentlyUpdating.frozen"
        @confirmed="toggleFrozen()"
    />

    <!-- Favorte -->
    <FavoriteToggle
        :contentType="contentTypes.Item"
        :objectId="item.id"
    />

    <!-- Private item -->
    <MenuItemWithConfirm
        v-if="currentDesk.privateItemsEnabled"
        :confirmMessage="togglePrivateConfirmMessage"
        :disabled="!item.user_has_private_perm"
        :iconName="item.is_private ? 'LockClosed' : 'LockOpen'"
        :isRed="item.is_private"
        :label="$t(item.is_private ? 'itemIsPrivate' : 'itemIsPublic')"
        :loading="fieldsCurrentlyUpdating.is_private"
        :tooltip="
            item.user_has_private_perm
                ? null
                : $t('whoCanMakeAccessible', { author: item.owners_string })
        "
        @confirmed="toggleIsPrivate()"
    />

    <!--<ItemDetailTour class="menu-item" :buttonVisible="true"/>-->

    <a
        class="menu-item"
        :href="printUrl"
    >
        <Icon name="Print" />
        {{ $t("download") }} PDF
    </a>

    <button
        class="menu-item"
        @click="openOffPanel('addItem')"
    >
        <Icon name="Copy" />
        {{ $t("duplicate") }}
    </button>

    <MenuItemWithConfirm
        iconName="Trash"
        :isRed="true"
        :label="$t('sendToTrash')"
        loadingName="putInTrash"
        @confirmed="putInTrash()"
    />
</div>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import urls from "@js/urls"
import { Fragment } from "vue-fragment"
import PilotMixin from "@components/PilotMixin"

import { ToggleButton } from "vue-js-toggle-button"

import FavoriteToggle from "@views/favorites/FavoriteToggle"
import ItemDetailTour from "@components/demos/ItemDetailTour.vue"
import MenuItemWithConfirm from "@components/MenuItemWithConfirm"

export default {
    name: "ItemDetailOptions",
    mixins: [PilotMixin],
    components: {
        Fragment,
        ItemDetailTour,
        FavoriteToggle,
        MenuItemWithConfirm,
        ToggleButton,
    },
    data: () => ({
        toggleIsPrivateAsked: false,
    }),
    computed: {
        ...mapState("sharings", ["sharings"]),
        ...mapState("itemDetail", ["item", "openedDrawer", "fieldsCurrentlyUpdating"]),
        ...mapGetters("itemDetail", ["itemId"]),
        printUrl() {
            return urls.itemExport.format({ id: this.itemId }) + "?type=pdf"
        },
        togglePrivateConfirmMessage() {
            if (!this.item.user_has_private_perm) {
                return this.$t("whoCanMakeAccessible", { author: this.item.owners_string })
            }
            return this.$t(this.item.is_private ? "makeItemAccessible" : "makeItemPrivate")
        },
    },
    methods: {
        ...mapMutations("offPanel", ["openOffPanel"]),
        ...mapActions("itemDetail", [
            "toggleFrozen",
            "toggleIsPrivate",
            "putInTrash",
            "openDrawer",
            "closePanel",
        ]),
    },
    i18n: {
        messages: {
            fr: {
                freeze: "Verrouiller édition",

                history: "Historique des modifications",
                itemIsPrivate: "Contenu privé - rendre public",
                itemIsPublic: "Contenu public - rendre privé",
                makeItemAccessible:
                    "Vous allez rendre ce contenu accessible à toutes les personnes connectées à ce compte Pilot",
                makeItemPrivate:
                    "Vous allez rendre ce contenu accessible uniquement à vous, aux responsables du contenu, et aux administrateurs",
                print: "Imprimer",
                privateItemNotEnabled: "Cette fonctionnalité n'est pas activée sur votre desk",
                sendToTrash: "Mettre à la corbeille",
                translations: "Traductions",
                unfreeze: "Déverrouiller édition",
                unfreezeConfirmMessage: "Le contenu pourra à nouveau être édité.",
                whoCanMakeAccessible:
                    "Seuls {author} , un/e administrateur/trice ou un des responsables du contenu peuvent le rendre privé",
            },
            en: {
                freeze: "Lock edition",

                history: "Activity logs",
                itemIsPrivate: "Private Content - Click to make it public",
                itemIsPublic: "Public Content - Click to make it private",
                makeItemAccessible:
                    "You will make this content accessible to everyone connected to this Pilot account",
                makeItemPrivate:
                    "You will make this content accessible only to you, to the content owners, and to the administrators",
                print: "Print",
                privateItemNotEnabled: "This feature is not enabled on your desk",
                sendToTrash: "Send to trash",
                translations: "Translations",
                unfreeze: "Unlock edition",
                unfreezeConfirmMessage: "The content will be editable again",
                whoCanMakeAccessible:
                    "Only {author}, an administrator or a content manager can make it private",
            },
        },
    },
}
</script>

<style lang="scss">
.ItemDetailOptions {
    width: 22rem;
}
</style>
