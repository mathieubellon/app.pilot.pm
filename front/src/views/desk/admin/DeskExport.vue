<template>
<div class="DeskExport container w-full">
    <Loading name="fetchExports" />

    <div
        v-if="exportLaunched"
        class="font-semibold text-lg mb-4 text-green-500 rounded bg-green-100 p-4"
    >
        {{ $t("exportLaunched") }}
    </div>

    <div class="flex flex-col flex-grow w-full">
        <div class="flex flex-row flew-grow">
            <div class="w-1/4 font-bold">{{ $t("start") }}</div>
            <div class="w-1/4 font-bold">{{ $t("creator") }}</div>
            <div class="w-1/4 font-bold">{{ $t("state") }}</div>
            <div class="w-1/4 font-bold">{{ $t("resultFile") }}</div>
        </div>
        <div
            v-for="exportJob in exports"
            class="flex flex-row flew-grow"
        >
            <div class="w-1/4">{{ exportJob.created_at | dateTimeFormat }}</div>
            <div class="w-1/4"><UserDisplay :user="exportJob.created_by" /></div>
            <div class="w-1/4">{{ exportJob.state }}</div>
            <div class="w-1/4">
                <a
                    v-if="exportJob.result_url"
                    :href="exportJob.result_url"
                >
                    {{ exportJob.result_file_name | defaultVal("-") }}
                </a>
                <template v-else>-</template>
            </div>
        </div>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "DeskExport",
    mixins: [PilotMixin],
    computed: {
        ...mapState("desk", ["exports", "exportLaunched"]),
    },
    i18n: {
        messages: {
            fr: {
                creator: "Lancé par",
                exportLaunched:
                    "Votre export est en cours de préparation, une fois terminé je vous avertirai par email avec un lien de téléchargement. Ce lien sera aussi présent sur cette page",
                resultFile: "Fichier généré",
            },
            en: {
                creator: "Started by",
                exportLaunched:
                    "Your export is in progress, I will notify you by email upon completion. The link will also be available on this page.",
                resultFile: "Generated file",
            },
        },
    },
}
</script>
