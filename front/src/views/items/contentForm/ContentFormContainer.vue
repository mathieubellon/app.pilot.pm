<!--
BIG FAT WARNING : Please take care when modifying things here.
Some js code depends on the Item container for scroll and positioning ( ex: annotations ).
If you modify some html or css here, this code may breaks.
Please ensure that all features related to scroll and positioning still works after any modification here.

Related code is located in @js/items/utils.js
and @views/items/detail/itemDecorationBoxes.js
-->
<template>
<div class="CenterPane">
    <div
        v-if="desynchronized || isDisconnectedAfterInactivity"
        class="mt-8 text-center"
    >
        <p class="font-bold text-lg">{{ $t("disconnectedMessage") }}</p>
        <button
            class="button is-blue w-60 mt-4"
            @click="reloadPage"
        >
            {{ $t("reloadPage") }}
        </button>
    </div>
    <div
        v-else
        class="ContentFormContainer"
        :class="{ isDiff }"
    >
        <div class="ContentFormContainer__FormAndColumns">
            <slot />

            <!-- Editable annotations -->
            <div
                v-show="editable"
                class="ContentFormContainer__DecorationBoxesColumn"
            >
                <ItemDetailTextAnnotations :annotationManagers="annotationManagers" />
            </div>

            <!-- Read-only annotations -->
            <div
                v-show="!editable"
                class="ContentFormContainer__DecorationBoxesColumn"
            >
                <ItemDetailTextAnnotations
                    :annotationManagers="readOnlyAnnotationManagers"
                    :readOnly="true"
                />
            </div>
        </div>
    </div>

    <OffPanel
        name="remoteVersionRestoration"
        height="30%"
        position="top"
    >
        <div
            v-if="remoteVersionRestoration"
            slot="offPanelBody"
        >
            {{
                $t("remoteVersionRestoration", {
                    version: remoteVersionRestoration.restored_version,
                })
            }}
            <UserDisplay
                :user="remoteVersionRestoration.restored_by"
                :withAvatar="true"
            />
        </div>
    </OffPanel>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import ItemDetailTextAnnotations from "@views/items/contentForm/annotations/text/ItemDetailTextAnnotations"

export default {
    name: "ContentFormContainer",
    mixins: [PilotMixin],
    components: {
        ItemDetailTextAnnotations,
    },
    props: {
        editable: Boolean,
        isDiff: Boolean,
    },
    computed: {
        ...mapState("itemContentForm", [
            "isDisconnectedAfterInactivity",
            "annotationManagers",
            "readOnlyAnnotationManagers",
            "desynchronized",
            "remoteVersionRestoration",
        ]),
    },
    methods: {
        reloadPage() {
            document.location.reload()
        },
    },
    i18n: {
        messages: {
            fr: {
                disconnectedMessage:
                    "Vous n'êtes plus connecté. Rechargez la page pour reprendre l'édition.",
                reloadPage: "Recharger la page",
                remoteVersionRestoration: "La version {version} vient d'être restaurée par ",
            },
            en: {
                disconnectedMessage: "Connection lost. Reload the page to resume editing.",
                reloadPage: "Reload the page",
                remoteVersionRestoration: "The version {version} has been restored by ",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors";
@import "~@sass/business/items_vars.scss";
@import "~@sass/include_media.scss";

.CenterPane {
    @apply h-full flex justify-center p-4 w-full;
    @include media("<=tablet") {
        @apply p-0;
    }
}

/**
WARNING : For correct annotations positioning,
the max-width for .ContentFormContainer .ItemContentForm and .ItemContentReadOnly
MUST ALL BE THE SAME
**/
.ContentFormContainer {
    @apply w-full max-w-3xl;

    @include media("<=tablet") {
        @apply p-4;
    }
    @include media("<=phone") {
        @apply p-1;
    }
}

.ContentFormContainer__FormAndColumns {
    // This is CRITICAL for the decoration boxes to be positioned correctly
    position: relative; //
    ////////////////////
    @apply px-8 py-2 m-1 rounded bg-white shadow;
    @include media("<=phone") {
        @apply px-3;
    }
}

.ContentFormContainer.isDiff {
    @apply max-w-none;

    .ContentFormContainer__FormAndColumns {
        @apply p-0 bg-transparent border-none shadow-none;
    }
}

.ContentFormContainer__DecorationBoxesColumn {
    position: absolute;
    top: 0;
    z-index: 30;
    width: $widthDecorationBox;
    right: -$widthDecorationBox - $itemDecorationBoxGutter;
}
</style>
