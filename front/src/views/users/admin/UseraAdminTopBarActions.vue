<template>
<Fragment>
    <Popper
        triggerElementName="PopperRef"
        triggerType="click"
    >
        <template #triggerElement>
            <button
                class="button is-topbar"
                ref="PopperRef"
            >
                {{ $t("actions") }}
                <!-- The empty span is required to correctly align with flex display -->
                <span>
                    <Icon
                        class="caret"
                        name="ChevronDown"
                    />
                </span>
            </button>
        </template>

        <template #content>
            <div class="w-64">
                <div
                    v-if="exportStarted"
                    class="p-4 font-semibold text-green-500"
                >
                    ✓ {{ $t("exportStarted") }}
                </div>
                <MenuItemWithConfirm
                    v-else
                    :confirmButtonText="$t('confirmExportAll')"
                    :confirmMessage="$t('youWillBeNotifiedAfterExport')"
                    iconName="Export"
                    :label="$t('exportAll')"
                    loadingName="exportAllUsers"
                    @confirmed="exportAllUsers()"
                />
            </div>
        </template>
    </Popper>

    <button
        v-show="currentRouteName == 'actives' || currentRouteName == 'pending'"
        class="button is-blue"
        :disabled="maxUsersReached"
        @click="openOffPanel('UserInvitationPanel')"
    >
        <template v-if="maxUsersReached">{{ $t("maximumReached") }}</template>
        <template v-else>
            {{ $t("inviteNewUser") }}
        </template>
    </button>

    <button
        v-show="currentRouteName == 'teams'"
        class="button is-blue mb-4"
        @click="openOffPanel('teamForm')"
    >
        {{ $t("createTeam") }}
    </button>
</Fragment>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import urls from "@js/urls.js"
import { $httpX } from "@js/ajax.js"
import PilotMixin from "@components/PilotMixin"
import { Fragment } from "vue-fragment"

import MenuItemWithConfirm from "@components/MenuItemWithConfirm"

export default {
    name: "UseraAdminTopBarActions",
    mixins: [PilotMixin],
    components: {
        Fragment,
        MenuItemWithConfirm,
    },
    data: () => ({
        exportStarted: false,
    }),
    computed: {
        ...mapGetters("usersAdmin", ["maxUsersReached"]),
    },
    methods: {
        exportAllUsers() {
            $httpX({
                name: "exportAllUsers",
                method: "PUT",
                url: urls.usersExportAll,
                commit: this.$store.commit,
            }).then(() => (this.exportStarted = true))
        },
    },
    i18n: {
        messages: {
            fr: {
                createTeam: "Créer une équipe",
                inviteNewUser: "Nouvel utilisateur",
                exportAll: "Exporter tous les utilisateurs (.xlsx)",
                maximumReached: "Invitation impossible, maximum atteint",
            },
            en: {
                createTeam: "Create a team",
                inviteNewUser: "Invite new user",
                exportAll: "Export all users (.xlsx)",
                maximumReached: "Invitation impossible, maximum reached",
            },
        },
    },
}
</script>
