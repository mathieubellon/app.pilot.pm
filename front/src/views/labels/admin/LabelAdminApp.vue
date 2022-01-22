<template>
<MainLayout>
    <template #title>{{ $t("labels") }}</template>

    <template #actions>
        <button
            v-show="currentRouteName == 'labelsList'"
            class="button is-blue"
            @click="$refs.content.startLabelCreation()"
        >
            {{ $t("addLabel") }}
        </button>
    </template>

    <template #content>
        <div class="container mx-auto p-5">
            <transition
                slot="main"
                enter-active-class="animated animated-150 fadeIn"
                leave-active-class="animated animated-150 fadeOut"
                mode="out-in"
            >
                <router-view ref="content" />
            </transition>
        </div>
    </template>
</MainLayout>
</template>

<script>
import PilotMixin from "@components/PilotMixin"
import MainLayout from "@components/layout/MainLayout"

export default {
    name: "LabelAdminApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
    },
    i18n: {
        messages: {
            fr: {
                addLabel: "Ajouter un label",
            },
            en: {
                addLabel: "Add a label",
            },
        },
    },
}
</script>
