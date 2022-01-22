<template>
<div class="UsageLimitAlert">
    <div
        v-if="usageLimitName == 'advancedFeature' && !allowAdvancedFeatures"
        class="simple-panel"
    >
        {{ $t("advancedFeaturesNotAllowed") }}
        <br />
        <a :href="urls.subscriptionApp">{{ $t("upgradeSubscription") }}</a>
    </div>

    <div
        v-else-if="usageLimitReached(usageLimitName)"
        class="simple-panel"
    >
        {{
            $t("limitReached", { max_usage: usageLimit.max_usage_display, label: usageLimit.label })
        }}
        <br />
        <a :href="urls.subscriptionApp">{{ $t("upgradeSubscription") }}</a>
    </div>

    <div
        v-else-if="usageLimit.is_near_limit"
        class="simple-panel"
    >
        {{
            $t("nearLimit", {
                max_usage: usageLimit.max_usage_display,
                label: usageLimit.label,
                usage_left: usageLimit.usage_left_display,
            })
        }}
        <br />
        <a :href="urls.subscriptionApp">{{ $t("upgradeSubscription") }}</a>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import urls from "@js/urls"

export default {
    name: "UsageLimitAlert",
    mixins: [PilotMixin],
    props: {
        usageLimitName: String,
    },
    data: () => ({
        urls: urls,
    }),
    computed: {
        ...mapState("usageLimits", ["usageLimits"]),
        ...mapGetters("usageLimits", ["usageLimitReached", "allowAdvancedFeatures"]),
        usageLimit() {
            return this.currentDesk.usageLimits[this.usageLimitName]
        },
    },
    i18n: {
        messages: {
            fr: {
                advancedFeaturesNotAllowed:
                    "Votre licence ne donne pas accès à cette fonctionnalité",
                limitReached:
                    "Vous avez atteint la limite de {max_usage} {label} alloués par votre licence",
                nearLimit:
                    "Il vous reste {usage_left} {label} sur la la limite de {max_usage} {label} alloués par votre licence",
                upgradeSubscription: "Améliorer votre abonnement",
            },
            en: {
                advancedFeaturesNotAllowed:
                    "Your subscription does not grant access to this feature",
                upgradeSubscription: "Upgrade your subsription",
                limitReached:
                    "You reached the limit of {max_usage} {label} allowed by your subscription",
                nearLimit:
                    "You have {usage_left} {label} left on a maximum of {max_usage} {label} allowed by your subscription",
            },
        },
    },
}
</script>
