<template>
<header :class="headerClass">
    <template v-if="item.id">
        <div class="flex justify-between items-center w-full px-2 sm:px-8 pb-1">
            <div class="flex flex-col truncate w-full">
                <div class="truncate text-base font-bold">
                    {{ itemEditable.content.title ? itemEditable.content.title : $t("untitled") }}
                </div>

                <ItemRealtimeState
                    v-if="sharing.is_editable"
                    class="mt-0.5"
                />
            </div>

            <div class="flex">
                <ItemTableOfContents v-if="sharing.is_editable" />
                <div
                    v-if="currentRealtimeState == REALTIME_STATES.conflict"
                    class="button bg-purple-400 cursor-default"
                >
                    {{ $t("conflict") }}
                </div>
                <LanguageSwitcher class="sm:ml-2" />
            </div>
        </div>

        <div class="flex justify-between items-center px-2 sm:px-8 text-xs leading-tight h-6">
            <div class="flex-grow">
                <a @click="openOffPanel('sharingDetails')">
                    {{ $t("contentSharedBy") }} {{ sharing.created_by.email }}
                </a>
                ( {{ $t(sharing.is_editable ? "youCanEdit" : "youCanNotEdit") }} )
            </div>

            <div class="flex items-center justify-end">
                <ItemRealtimeUsers />
            </div>
        </div>

        <div class="flex justify-between items-center px-2 sm:px-8 py-2">
            <router-link
                v-if="sharing.type != 'item'"
                class="self-start -ml-2 -mt-1"
                :to="{ name: 'sharing' }"
            >
                <Icon
                    class="-mt-0.5 -mr-1"
                    name="ChevronLeft"
                />
                {{ $t("backToList") }}
            </router-link>
            <span v-else />

            <!-- Only sharings sent to a specific recipient can have feedbacks -->
            <SharedItemFeedback v-if="sharing.email" />
        </div>

        <ItemSavingRecoveryBar />
        <ItemFrozenBar :item="item" />
    </template>

    <div
        v-else
        class="text-lg font-bold p-4 h-24 flex items-center justify-center"
    >
        <BarLoader class="w-2/3" />
    </div>

    <OffPanel
        name="sharingDetails"
        position="top"
    >
        <div slot="offPanelBody">
            <p v-if="sharing.comment">
                {{ $t("message") }} :
                <cite>{{ sharing.comment }}</cite>
            </p>
            <div>
                <div>
                    <b>{{ $t("publicationDate") }} :</b>
                    {{ item.publication_dt | dateFormat }}
                </div>
                <div v-if="item.channels_names">
                    <b>{{ $t("channels") }} :</b>
                    {{ item.channels_names.join(", ") }}
                </div>
                <div v-if="item.project">
                    <b>{{ $t("project") }} :</b>
                    {{ item.project.name }}
                </div>

                <hr class="my-2" />
                <h6 class="font-bold">{{ $t("assetsLinked") }}</h6>
                <div class="AssetList">
                    <div
                        v-for="asset in item.assets"
                        class="AssetElement GridView"
                    >
                        <AssetPreview
                            :asset="asset"
                            context="shared"
                        />
                        <div class="AssetElement__Title my-2">
                            <a :href="asset.file_url">{{ asset.name }}</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </OffPanel>
</header>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import PilotMixin from "@components/PilotMixin"
import { REALTIME_STATES } from "@/store/modules/ItemContentFormStore.js"

import LanguageSwitcher from "@components/LanguageSwitcher.vue"
import ItemRealtimeState from "@views/items/detail/header/ItemRealtimeState.vue"
import ItemRealtimeUsers from "@views/items/detail/header/ItemRealtimeUsers"
import SharedItemFeedback from "./SharedItemFeedback"
import ItemTableOfContents from "@views/items/detail/header/ItemTableOfContents"
import AssetPreview from "@views/assets/AssetPreview"
import ItemSavingRecoveryBar from "@views/items/detail/ItemSavingRecoveryBar.vue"
import ItemFrozenBar from "@views/items/detail/ItemFrozenBar.vue"

export default {
    name: "SharedItemHeader",
    mixins: [PilotMixin],
    components: {
        AssetPreview,
        LanguageSwitcher,
        ItemRealtimeState,
        ItemRealtimeUsers,
        SharedItemFeedback,
        ItemTableOfContents,
        ItemSavingRecoveryBar,
        ItemFrozenBar,
    },
    data: () => ({
        REALTIME_STATES,
    }),
    computed: {
        ...mapState(["sharing"]),
        ...mapState("sharedItem", ["item"]),
        ...mapState("itemContentForm", ["validation", "itemEditable"]),
        ...mapGetters("itemContentForm", ["currentRealtimeState"]),
        headerClass() {
            if (this.currentRealtimeState == REALTIME_STATES.conflict) {
                return "bg-purple-100"
            }
            /*
            else if( this.isFormInvalid ){
                return 'bg-red-50'
            }
            */
        },
    },
    i18n: {
        messages: {
            fr: {
                assetsLinked: "Fichiers liés au contenu",
                backToList: "Retour à la liste",
                contentSharedBy: "Contenu partagé par",
                itemShared: "Contenu partagé",
                message: "Message",
                youCanEdit: "Modification possible",
                youCanNotEdit: "Lecture seule",
            },
            en: {
                assetsLinked: "Assets linked",
                backToList: "Back to the list",
                contentSharedBy: "Content shared by",
                itemShared: "Shared content",
                message: "Message",
                youCanEdit: "Edit allowed",
                youCanNotEdit: "Read only",
            },
        },
    },
}
</script>
