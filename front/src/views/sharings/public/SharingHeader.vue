<template>
<div class="px-2 sm:px-8">
    <div class="flex justify-between">
        <div>
            <div>
                {{ $t("sharingOf") }} {{ $t("sharingType." + sharing.type) }}
                <span
                    v-if="sharing.project"
                    class="font-bold"
                >
                    {{ sharing.project.name }}
                </span>
                <span
                    v-if="sharing.channel"
                    class="font-bold"
                >
                    {{ sharing.channel.name }}
                </span>
                <span
                    v-if="sharing.saved_filter"
                    class="font-bold"
                >
                    {{ sharing.saved_filter.title }}
                </span>
            </div>
            <div v-if="sharing.email">
                {{ $t("sentTo") }}
                <span class="font-bold">{{ sharing.email }}</span>
            </div>
            <div>
                {{ $t("the") }}
                <span class="font-bold">{{ sharing.created_at | dateFormat }}</span>
            </div>
            <div>
                {{ $t("by") }}
                <span class="font-bold">{{ sharing.created_by.username }}</span>
            </div>
        </div>

        <LanguageSwitcher />
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import LanguageSwitcher from "@components/LanguageSwitcher.vue"

export default {
    name: "SharingHeader",
    mixins: [PilotMixin],
    components: {
        LanguageSwitcher,
    },
    computed: {
        ...mapState(["sharing"]),
    },
    i18n: {
        messages: {
            fr: {
                sharingOf: "Partage de",
                sharingType: {
                    calendar: "calendrier",
                    channel: "contenus de canal",
                    list: "liste de contenus",
                    project: "contenus de projet",
                },
                sentTo: "envoyé à",
                the: "le",
            },
            en: {
                sharingOf: "Sharing of",
                sharingType: {
                    calendar: "a calendar",
                    channel: "channel's contents",
                    list: "a list of content",
                    project: "project's contents",
                },
                sentTo: "sent to",
                the: "the",
            },
        },
    },
}
</script>
