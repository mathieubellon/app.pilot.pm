<template>
<div class="flex items-center">
    <div
        v-if="isPageUnloading"
        class="text-xs leading-tight py-0"
    >
        {{ $t("unloading") }}
    </div>
    <template v-else>
        <Popper
            ref="desynchronized"
            triggerElementName="RealtimeStatus"
            triggerType="click"
            :visibleArrow="false"
        >
            <template #triggerElement>
                <div
                    class="cursor-pointer"
                    ref="RealtimeStatus"
                >
                    <div
                        v-if="currentRealtimeState == REALTIME_STATES.connected"
                        class="flex flex-no-wrap min-w-0"
                    >
                        <span class="mr-1">{{ $t("lastEditBy") }}</span>
                        <span
                            v-if="lastEditor && lastEditor.id"
                            class="mr-1"
                        >
                            @{{ lastEditor.username }}
                        </span>
                        <span
                            v-else
                            class="mr-1"
                        >
                            {{ lastEditor }}
                        </span>
                        <span>{{ lastEditionDatetime | timeAgo }}</span>
                    </div>
                    <template v-if="currentRealtimeState == REALTIME_STATES.saving">
                        {{ $t("savingInProgress") }}
                    </template>
                    <template v-if="currentRealtimeState == REALTIME_STATES.conflict">
                        {{ $t("conflictToResolve") }}
                    </template>
                    <template v-if="currentRealtimeState == REALTIME_STATES.desynchronized">
                        {{ $t("cannotSaveReloadPage") }}
                    </template>
                </div>
            </template>

            <template #content>
                <div class="flex flex-col max-w-sm z-40 whitespace-normal">
                    {{ currentStateMessage.title }}
                    <div
                        v-for="state in stateMessages"
                        class="flex items-center w-full mb-1 p-2 rounded-sm text-sm font-medium leading-tight"
                        :class="[state.backgroundColor, state.accentColor]"
                        ref="RealtimeStatus"
                    >
                        <div class="flex flex-shrink-0">
                            <svg
                                class="-ml-1 mr-1.5 h-2 w-2"
                                :class="state.accentColor"
                                fill="currentColor"
                                viewBox="0 0 8 8"
                            >
                                <circle
                                    cx="4"
                                    cy="4"
                                    r="3"
                                />
                            </svg>
                        </div>
                        <div>
                            <div class="font-bold">{{ state.title }}</div>
                            <div>{{ state.explain }}</div>
                        </div>
                    </div>
                </div>
            </template>
        </Popper>
    </template>
</div>
</template>

<script>
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

import PilotMixin from "@components/PilotMixin"
import { REALTIME_STATES } from "@/store/modules/ItemContentFormStore.js"

export default {
    name: "ItemRealtimeState",
    mixins: [PilotMixin],
    data: () => ({
        isPageUnloading: false,
        REALTIME_STATES,
    }),
    computed: {
        ...mapState("itemContentForm", ["lastEditor", "lastEditionDatetime"]),
        ...mapGetters("itemContentForm", ["currentRealtimeState"]),
        stateMessages() {
            return {
                /*Après chargement item, init connexion websocket*/
                connecting: {
                    title: this.$t("connecting"),
                    explain: this.$t("connectingExplanation"),
                    accentColor: "text-gray-800",
                    backgroundColor: "bg-gray-100",
                },
                /*
                Connecté via websocket

                ou

                On a pas réussi a se connecter au mode webscoket, donc on passe en mode dégradé :
                on peut pas t'afficher le contenu temps réél
                mais tu peux faire des modifs en espérant que tu sois pas désynchro, à l'ancienne.
                */
                connected: {
                    title: this.$t("connected"),
                    explain: this.$t("connectedExplanation"),
                    accentColor: "text-green-800",
                    backgroundColor: "bg-green-100",
                },
                /*Sauvegarde / synchro*/
                saving: {
                    title: this.$t("saving"),
                    explain: this.$t("savingExplanation"),
                    accentColor: "text-blue-800",
                    backgroundColor: "bg-blue-100",
                },
                /*Sur les champs prosemirror system de rebase, mais sur tous les autres champs on peut avoir
                une sauveagrde simultanée, donc règle du premier arrivé premier servi, donc le second on lui
                demande soit de prendre la modif du serveur soit d'écraser celle du serveur avec la sienne*/
                conflict: {
                    title: this.$t("conflict"),
                    explain: this.$t("conflictExplanation"),
                    accentColor: "text-purple-800",
                    backgroundColor: "bg-purple-100",
                },
                /* Connexion websocket perdue, mode dégradé,
                lancement sauvegarde en XHR et serveur répond "contenu pas à jour"
                ( le contenu a évolué depuis qu'on a loadé la page )

                ou

                4h d'inactivité, pas considéré comme présent donc on coupe la connexion
                côté serveur, le client le détecte.
                */
                desynchronized: {
                    title: this.$t("desynchronized"),
                    explain: this.$t("desynchronizedExplanation"),
                    accentColor: "text-red-800",
                    backgroundColor: "bg-red-100",
                },
            }
        },
        currentStateMessage() {
            return this.stateMessages[this.currentRealtimeState]
        },
    },
    created() {
        this.onBeforeUnload = () => {
            this.isPageUnloading = true
            // Unloading may be cancelled if there's still pending changes.
            // In this case, we'll get back to a nominal state after 2 seconds
            setTimeout(() => (this.isPageUnloading = false), 2000)
        }
        $(window).on("beforeunload", this.onBeforeUnload)
    },
    beforeDestroy() {
        $(window).off("beforeunload", this.onBeforeUnload)
    },
    i18n: {
        messages: {
            fr: {
                cannotSave: "Sauvegarde impossible",
                cannotSaveReloadPage: "Sauvegarde impossible, rechargez la page",
                conflict: "Conflit",
                conflictExplanation:
                    "Il y a eu un conflit sur l'édition simultanée d'un champ avec un autre utilisateur",
                conflictToResolve:
                    "Un des champs est en conflit. Choicissez une version avant de reprendre la sauvegarde",
                connected: "Sauvegardé",
                connectedExplanation:
                    "Votre copie est à jour (vos modifications ont été prises en compte ou vous avez reçues les plus récentes)",
                connectedUsers: "Connectés",
                connecting: "Connexion au serveur temps réel",
                connectingExplanation: "Connection en cours au serveur d'édition en temps réél",
                desynchronized: "Désynchronisé",
                desynchronizedExplanation:
                    "Vous n'êtes plus connecté. Rechargez la page pour reprendre l'édition.",
                lastEditBy: "Modifié par",
                saving: "Sauvegarde",
                savingExplanation:
                    "Une sauvegarde est en cours, vos changements sont synchronisés avec le serveur. Dans le cas de contenus très longs cela peut prendre plusieurs secondes.",
                savingInProgress: "Sauvegarde en cours",
            },
            en: {
                cannotSave: "Cannot save",
                cannotSaveReloadPage: "Cannot save, reload the page",
                conflict: "Conflict",
                conflictExplanation:
                    "There was a conflict over simultaneous editing of a field with another user.",
                conflictToResolve:
                    "One of the fields is in conflict. Select a version to continue the saving",
                connected: "Saved",
                connectedExplanation:
                    "Your copy is up to date (your modifications have been taken into account or you have received the most recent ones)",
                connectedUsers: "Connected users",
                connecting: "Connection to the realtime server",
                connectingExplanation: "Connection to realtime server in progress ",
                desynchronized: "Desynchronized",
                desynchronizedExplanation:
                    "You are disconnected. Reload the page to continue the edition.",
                lastEditBy: "Edited by",
                saving: "Saving",
                savingExplanation:
                    "A backup is in progress, your changes are synchronized with the server. In the case of very long content it can take several seconds",
                savingInProgress: "Saving in progress",
            },
        },
    },
}
</script>
