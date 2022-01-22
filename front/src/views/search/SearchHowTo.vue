<template>
<div>
    <Popper
        position="auto"
        triggerElementName="PopperRef"
        triggerType="hover"
    >
        <template #triggerElement>
            <button
                class="text-gray-600 underline text-sm"
                ref="PopperRef"
            >
                {{ $t("usageGuideTitle") }}
            </button>
        </template>

        <template #content>
            <div>
                <div class="mt-5 rounded text-base p-2">
                    <h2 class="text-base mb-3 font-medium">{{ $t("usageGuideIntro") }}</h2>
                    <div>
                        <strong>{{ $t("examples") }}</strong>
                    </div>
                    <div class="queryExample">
                        <div class="query">{{ $t("ulysse") }}</div>
                        <div>{{ $t("basicSearch") }}</div>
                    </div>
                    <div class="queryExample">
                        <div class="flex items-center">
                            <div class="query">{{ $t("ulysseTroy") }}</div>
                            &nbsp;
                            <div class="query">{{ $t("ulysseORTroy") }}</div>
                        </div>
                        <div>{{ $t("basicORSearch") }}</div>
                    </div>
                    <div class="queryExample">
                        <div class="query">{{ $t("TrojanANDhorse") }}</div>
                        <div>{{ $t("basicANDSearch") }}</div>
                    </div>
                    <div class="queryExample">
                        <div class="query">Achille +Ulysse</div>
                        <div>{{ $t("mandatoryTermSearch") }}</div>
                    </div>
                    <div class="queryExample">
                        <div class="query">-Achille +Ulysse</div>
                        <div>{{ $t("excludeTermSearch") }}</div>
                    </div>
                    <div class="queryExample">
                        <div class="query">{{ $t("TrojanHorse") }}</div>
                        <div>{{ $t("fullSentenceSearch") }}</div>
                    </div>
                    <div class="queryExample">
                        <div class="query">project:Illiad</div>
                        <div>{{ $t("searchField") }}</div>
                        <i>{{ $t("availableFields") }}</i>
                    </div>
                </div>
            </div>
        </template>
    </Popper>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"
export default {
    name: "SearchHowTo",
    mixins: [PilotMixin],
    i18n: {
        messages: {
            fr: {
                usageGuideTitle: "Mode d'emploi",
                usageGuideIntro:
                    "La recherche s'effectue plein texte. Elle est insensible à la casse ou aux accents.",
                examples: "Exemples",
                ulysse: "ulysse",
                basicSearch: "Recherche les documents contenant le mot-clé 'ulysse'",
                ulysseTroy: "ulysse Troie",
                ulysseORTroy: "ulysse OR Troie",
                basicORSearch: "Recherche les documents contenant 'ulysse' OU 'Troie'",
                TrojanANDhorse: "cheval AND Troie",
                basicANDSearch: "Recherche les documents contenant 'cheval' ET 'Troie'",
                mandatoryTermSearch:
                    "Recherche les documents contenant obligatoirement 'Ulysse' et optionnellement 'Achille'",
                excludeTermSearch:
                    "Recherche les documents contenant obligatoirement 'Ulysse' et ne contenant PAS 'Achille'",
                TrojanHorse: '"Cheval de Troie"',
                fullSentenceSearch:
                    "Recherche les documents contenant la phrase exacte 'Cheval de Troie'",
                searchField: "Recherche les documents dont le champ projet contient 'Illiad'",
                availableFields:
                    "Les champs à votre disposition pour le filtrage sont : project, channel, targets, tags, publication_dt, language",
            },
            en: {
                usageGuideTitle: "Usage guide",
                usageGuideIntro: "Search is plain text, case insensitive",
                examples: "Examples",
                ulysse: "ulysse",
                basicSearch: "Search documents for keyword 'ulysse'",
                ulysseTroy: "ulysse Troy",
                ulysseORTroy: "ulysse OR Troy",
                basicORSearch: "Search documents for keywords 'ulysse' OR 'Troy'",
                TrojanANDhorse: "horse AND Trojan",
                basicANDSearch: "Search documents for keywords 'horse' AND 'Trojan'",
                mandatoryTermSearch:
                    "Search documents that must contain 'ulysse' and may contain 'Achille'",
                excludeTermSearch:
                    "Search documents that must contain 'ulysse' and must not contain 'Achille'",
                TrojanHorse: '"Trojan Horse"',
                fullSentenceSearch: "Search for documents with the exact sentence 'Trojan horse'",
                searchField: "Search for documents where field 'project' contains 'Illiad'",
                availableFields:
                    "You can use the following fields : project, channel, targets, tags, publication_dt, language",
            },
        },
    },
}
</script>

<style lang="scss">
.queryExample {
    @apply my-3 flex flex-col justify-start items-start;
    .query {
        @apply bg-black p-1 rounded text-gray-300 font-mono text-sm;
    }
}
</style>
