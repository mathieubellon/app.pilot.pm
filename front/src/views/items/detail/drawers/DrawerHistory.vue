<template>
<div class="ItemDrawer DrawerHistory">
    <div></div>

    <div class="ItemDrawer__Header">
        {{ $t("versions") }}

        <div
            class="ItemDrawer__Header__Close"
            @click="closePanel()"
        >
            {{ $t("close") }}
        </div>
    </div>

    <Loadarium name="editSessions">
        <a
            v-if="getMinorVersion(lastEditSession) > 0 && !createMajorVersionRequested"
            class="button is-outlined w-full mb-4"
            @click="requestCreateMajorVersion()"
        >
            {{ $t("createMajorVersion") }}
        </a>
        <div
            v-if="createMajorVersionRequested"
            class="mb-4"
        >
            <SmartButtonSpinner
                class="button is-blue w-full mb-1"
                name="createMajorVersion"
                :timeout="1500"
                @click="createMajorVersion()"
            >
                {{ $t("confirm") }}
            </SmartButtonSpinner>
            <a
                class="button is-white w-full"
                @click="cancelCreateMajorVersion()"
            >
                {{ $t("cancel") }}
            </a>
        </div>

        <DrawerHistoryElement
            v-for="editSession in editSessions"
            :editSession="editSession"
            :key="editSession.id"
        />
    </Loadarium>

    <div class="help-text">
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="Layers"
            />
            <span>{{ $t("howItWorks") }}</span>
        </div>
        <div class="help-text-content">{{ $t("explainSession") }}</div>
        <div class="help-text-content">{{ $t("explainEndSession") }}</div>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import DrawerHistoryElement from "./DrawerHistoryElement"

export default {
    name: "DrawerHistory",
    mixins: [PilotMixin],
    components: {
        DrawerHistoryElement,
    },
    computed: {
        ...mapState("itemDetail", ["editSessions", "createMajorVersionRequested"]),
        ...mapGetters("itemDetail", ["isCurrentVersion", "lastEditSession", "getMinorVersion"]),
    },
    methods: {
        ...mapMutations("itemDetail", ["requestCreateMajorVersion", "cancelCreateMajorVersion"]),
        ...mapActions("itemDetail", ["createMajorVersion", "closePanel"]),
    },
    i18n: {
        messages: {
            fr: {
                explainEndSession:
                    "Une session commence à la première modification et se termine après 15mn d'inactivité",
                explainSession:
                    'Les différentes versions du contenu se créent automatiquement à mesure que vous éditez le contenu durant une "session de travail"',
                howItWorks: "Comment ça marche?",
                createMajorVersion: "Créer une version majeure",
            },
            en: {
                explainEndSession:
                    "A session starts at the first modification and ends after 15 minutes of inactivity",
                explainSession:
                    'The different versions of the content are automatically created as you edit the content during a "working session"',
                howItWorks: "How does it work?",
                createMajorVersion: "Create a major version",
            },
        },
    },
}
</script>
