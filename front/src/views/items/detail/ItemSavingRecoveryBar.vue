<template>
<div
    v-if="savingState && savingState.recoveryState"
    class="p-2"
    :class="{
        'bg-purple-700 text-purple-100': savingState.isReconnecting || savingState.isXhr,
        'bg-red-700 text-red-100': savingState.isFailed,
        'bg-green-600 text-green-100': savingState.isResolved,
    }"
>
    <template v-if="savingState.isReconnecting">
        <Icon
            class="mr-2"
            name="Info"
        />
        {{ $t("reconnecting") }}
        <br />
        <BarLoader
            class="mt-2 ml-10 w-full"
            :color="colors.purple100"
        />
    </template>

    <template v-else-if="savingState.isXhr">
        <Icon
            class="mr-2"
            name="Info"
        />
        {{ $t("reconnectingXhr") }}
        <br />
        <BarLoader
            class="mt-2 ml-10 w-full"
            :color="colors.purple100"
        />
    </template>

    <template v-else-if="savingState.isFailed">
        <Icon
            class="mr-2"
            name="Frown"
        />
        {{ $t("failed") }}
    </template>

    <div
        v-else-if="savingState.isResolved"
        class="flex justify-between items-center w-full"
    >
        <span>
            <Icon
                class="mr-2"
                name="Check"
            />
            {{ $t("recovered") }}
        </span>

        <button
            class="button is-white is-small"
            @click="setSavingState(null)"
        >
            {{ $t("close") }}
        </button>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ItemSavingRecoveryBar",
    mixins: [PilotMixin],
    computed: {
        ...mapState("itemContentForm", ["savingState"]),
    },
    methods: {
        ...mapMutations("itemContentForm", ["setSavingState"]),
    },
    i18n: {
        messages: {
            fr: {
                failed:
                    "Nous n'avons pas réussi à sauvegarder vos modifications. Il y a probablement un problème sur le réseau. Vous pouvez essayer de recharger la page.",
                reconnecting:
                    "La sauvegarde est anormalement longue. Nous allons essayer à nouveau. Merci de patienter pendant la reconnexion, sans quitter la page.",
                reconnectingXhr:
                    "Nous essayons maintenant de sauvegarder par un autre moyen, merci de rester sur la page encore un peu.",
                recovered:
                    "Ouf, nous avons réussi à sauvegarder, vous pouvez continuer l'édition du contenu.",
            },
            en: {},
        },
    },
}
</script>
