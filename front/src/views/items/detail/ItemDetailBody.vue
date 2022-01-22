<!--
!!! Varúð !!!
It's critical to use a v-show on the ItemContentForm, and all its parent hierarchy , instead of a v-if,
so the Editor is always available to integrate remote realtime changes,
even when not visible because the user is viewing a diff.
-->

<template>
<div class="ItemDetailBody">
    <div
        v-if="!item.user_has_access"
        class="ItemDetailBody__privateItemInaccessible alert-panel is-yellow"
    >
        <p>{{ $t("itemIsPrivate") }}</p>
        <p>{{ $t("accessOnlyBy", { owners: item.owners_string }) }}</p>
    </div>

    <template v-else>
        <ItemContentMergeTool v-if="isMergeToolActive" />

        <transition
            name="drawer"
            enter-active-class="animated fadeIn"
            leave-active-class="animated fadeOut"
        >
            <div
                v-show="openedDrawer !== null"
                class="ItemDetailBody__drawer"
            >
                <transition
                    name="drawer-fade"
                    mode="out-in"
                >
                    <component v-bind:is="DRAWER_COMPONENTS[openedDrawer]" />
                </transition>

                <!--
                We make a special case for the DrawerAssets which must always be present in the DOM,
                so a long upload will not be interrupted if the user close the drawer.
                We use a v-show, so the components is never removed from the DOM by the v-bind:is
                -->
                <transition name="drawer-fade">
                    <DrawerAssets v-show="openedDrawer == 'assets'" />
                </transition>
            </div>
        </transition>

        <!--
        BIG FAT WARNING : Please take care when modifying things here and inside ContentFormContainer.
        Some js code depends on the Item container for scroll and positioning  ( ex: annotations ).
        If you modify some html or css here, this code may breaks.
        Please ensure that all features related to scroll and positioning still works after any modification here.

        Related code is located in @js/items/utils.js
        and @views/items/detail/itemDecorationBoxes.js
        -->
        <div
            v-show="!isMergeToolActive"
            class="ItemDetailBody__content"
            :class="{ 'bg-white': itemReadOnly.isDiff }"
        >
            <ContentFormContainer
                :editable="editable"
                :isDiff="itemReadOnly.isDiff"
            >
                <!--
                The ItemContentForm component must always be in the virtual DOM to receive
                realtime modifications.
                DO NOT USE v-if !
                -->
                <ItemContentForm v-show="editable && !item.in_trash && !item.frozen" />

                <template v-if="(itemReadOnly && !editable) || item.in_trash || item.frozen">
                    <ItemContentDiff
                        v-if="itemReadOnly.isDiff"
                        :itemReadOnly="itemReadOnly"
                    />
                    <template v-else>
                        <div
                            v-show="diffComputation"
                            class="sticky top-0 z-50 bg-yellow-100 w-full p-2 font-bold text-lg"
                        >
                            {{ $t("diffCanBeLong") }}
                            <BarLoader class="w-full mt-2" />
                        </div>
                        <ItemContentReadOnly :itemReadOnly="itemReadOnly" />
                    </template>
                </template>
            </ContentFormContainer>
        </div>
    </template>
</div>
</template>

<script>
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import realtime from "@js/realtime"
import PilotMixin from "@components/PilotMixin"

import ItemContentForm from "@views/items/detail/ItemContentForm"
import ItemContentReadOnly from "@views/items/contentForm/ItemContentReadOnly"
import ItemContentDiff from "@views/items/detail/diff/ItemContentDiff"
import ItemContentMergeTool from "@views/items/detail/mergeTool/ItemContentMergeTool"
import ItemDetailTextAnnotations from "@views/items/contentForm/annotations/text/ItemDetailTextAnnotations"
import ContentFormContainer from "@views/items/contentForm/ContentFormContainer"

import DrawerInformations from "./drawers/DrawerInformations"
import DrawerTranslations from "./drawers/DrawerTranslations"
import DrawerHistory from "./drawers/DrawerHistory"
import DrawerActivity from "./drawers/DrawerActivity"
import DrawerTasks from "./drawers/DrawerTasks"
import DrawerAssets from "./drawers/DrawerAssets"

const DRAWER_COMPONENTS = {
    infos: DrawerInformations,
    history: DrawerHistory,
    activity: DrawerActivity,
    tasks: DrawerTasks,
    // 'assets': DrawerAssets,
    translations: DrawerTranslations,
}

export default {
    name: "ItemDetailBody",
    mixins: [PilotMixin],
    components: {
        ItemContentDiff,
        ItemContentForm,
        ItemContentReadOnly,
        ItemContentMergeTool,
        ItemDetailTextAnnotations,
        ContentFormContainer,
        DrawerAssets,
    },
    data: () => ({
        isPageUnloading: false,
        diffComputation: false,
        DRAWER_COMPONENTS,
        realtime,
    }),
    computed: {
        ...mapState("itemDetail", [
            "item",
            "itemReadOnly",
            "openedDrawer",
            "editable",
            "isMergeToolActive",
        ]),
        ...mapState("loading", ["loadingInProgress"]),
    },
    methods: {
        ...mapActions("itemDetail", ["alignDecorationBoxes"]),
    },
    watch: {
        loadingInProgress: {
            deep: true,
            handler: function (loadingInProgress) {
                if (loadingInProgress.fetchItemDiff) {
                    this.diffComputation = true
                }
                if (loadingInProgress.fetchEditSession) {
                    this.diffComputation = false
                }
            },
        },
    },
    created() {
        this.onBeforeUnload = () => {
            this.isPageUnloading = true
        }
        $(window).on("beforeunload", this.onBeforeUnload)
    },
    beforeDestroy() {
        $(window).off("beforeunload", this.onBeforeUnload)
    },
    i18n: {
        messages: {
            fr: {
                accessOnlyBy:
                    "Seuls {owners} ou un/e administrateur/trice  peuvent y accéder et le rendre public",
                annotationsToReplace: "Annotations à replacer",
                diffCanBeLong:
                    "Calcul des différences en cours, cela peut être long, merci de patienter...",
                itemIsPrivate: "Ce contenu est privé.",
                saveBeforeAnnotate:
                    " Vous ne pouvez pas annoter tant que le contenu est en cours d'édition. Vous devez sauvegarder une version pour annoter",
            },
            en: {
                accessOnlyBy: "Only {owners} or an administrator can access it and make it public",
                annotationsToReplace: "Annotations to replace",
                diffCanBeLong:
                    "Diff computation in progress, this can be long, thanks to be patient...",
                itemIsPrivate: "This content is private.",
                saveBeforeAnnotate:
                    "You can not annotate while the content is being edited. You must save a version to annotate",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/include_media.scss";
@import "~@sass/colors";
@import "~@sass/business/items_vars.scss";
@import "~@sass/mixins.scss";

/**
BIG FAT WARNING : Please take care when modifying things here.
Some js code depends on the Item container for scroll and positioning.
If you modify some html or css here, this code may breaks.
Please ensure that all features related to scroll and positioning still works after any modification here.

Related code is located in @js/items/utils.js
*/

.ItemDetailBody {
    @apply flex h-full;
    overflow: hidden;

    .ItemDetailBody__content {
        @apply flex mx-auto;
        flex-basis: 100%;
        overflow-y: auto;
    }
    .ItemDetailBody__drawer {
        @apply shadow-inner min-h-0 flex flex-col min-h-0 px-2 overflow-y-auto border-r border-gray-200 bg-gray-50;
        flex-basis: 700px;
        @include transition(opacity 0.2s ease);

        @include media("<=tablet") {
            @apply absolute inset-0;
            z-index: 80;
        }
    }
}

.ItemDetailBody__privateItemInaccessible {
    display: table;
    margin-left: auto;
    margin-right: auto;
    text-align: center;
    font-size: 1.2em;
}

.drawer-fade-enter-active,
.drawer-fade-leave-active {
    transition: opacity 0.2s ease;
}
.drawer-fade-enter, .drawer-fade-leave-to
    /* .drawer-fade-leave-active avant la 2.1.8 */ {
    opacity: 0;
}

// Special transition handling because of the special case for DrawerAssets
.DrawerAssets {
    &.drawer-fade-enter-active {
        transition-delay: 0.2s;
    }
    &.drawer-fade-leave-active {
        transition: 0s;
    }
    &.drawer-fade-leave {
        display: none;
    }
}

.ItemDrawer {
    @apply px-6 py-4 w-full;

    .ItemDrawer__Header {
        @apply flex items-center w-full justify-between text-gray-900 font-bold text-lg mb-5;
    }

    .ItemDrawer__Header__Close {
        @apply font-medium text-sm cursor-pointer;

        &:hover {
            @apply text-blue-600;
        }
    }
}
</style>
