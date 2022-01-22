<template>
<MainLayout>
    <template slot="title">
        {{ $t("sharings") }}
    </template>

    <div
        class="SharingAdminApp container mx-auto p-5"
        slot="content"
    >
        <Loadarium name="fetchSharingsList" />

        <div class="flex flex-grow justify-end">
            <Pagination
                v-if="sharings.length > 0 && !loadingInProgress.fetchSharingsList"
                :pagination="pagination"
                @pageChange="apiSource.setPage"
            />
        </div>

        <SharingsListBulkbar
            :pagination="pagination"
            :sharings="sharings"
            @deactivated="removeSharingsById"
        />

        <transition-group
            v-if="!loadingInProgress.fetchSharingsList"
            class="mt-2"
            leave-active-class="animated animated-500 fadeOutLeft"
            tag="div"
        >
            <div
                v-for="sharing of sharings"
                class="AdminList__listElement"
                :key="sharing.id"
            >
                <div class="mr-4">
                    <input
                        :checked="isSelectedForBulkAction(sharing)"
                        type="checkbox"
                        @change="toggleForBulkAction(sharing)"
                    />
                </div>

                <div class="flex flex-col flex-grow">
                    <SmartLink
                        class="text-gray-900 text-base font-semibold"
                        :to="sharing.url"
                    >
                        {{ sharedObjectRepr(sharing) }}
                    </SmartLink>
                    <div class="text-sm mt-1">
                        <span class="text-gray-500 font-semibold">
                            {{ sharing.created_at | dateFormat }}
                            &bullet;
                        </span>

                        <UserDisplay
                            aClass="border rounded px-1 mr-1 bg-indigo-50 hover:bg-indigo-100"
                            :user="sharing.created_by"
                        />

                        <span
                            v-if="sharing.email"
                            class="border rounded px-1 bg-teal-50"
                        >
                            {{ sharing.email }}
                        </span>
                        <span
                            v-else
                            class="border rounded px-1 bg-green-100"
                        >
                            {{ $t("sharingLink") }}
                        </span>
                    </div>
                </div>

                <div
                    class="flex flex-col items-center justify-center w-20 ml-2 text-xs"
                    :class="sharing.is_editable ? 'text-gray-800' : 'text-gray-400'"
                >
                    <template v-if="sharing.is_editable">
                        <Icon
                            name="Edit"
                            size="20px"
                        />
                        {{ $t("editable") }}
                    </template>
                    <template v-else>
                        <Icon
                            name="Eye"
                            size="20px"
                        />
                        {{ $t("readOnly") }}
                    </template>
                </div>

                <div
                    class="flex flex-col items-center justify-center w-20 ml-2 text-xs"
                    :class="sharing.password ? 'text-gray-800' : 'text-gray-400'"
                >
                    <template v-if="sharing.password">
                        <Icon
                            name="LockClosed"
                            size="20px"
                        />
                        {{ $t("password") }}
                    </template>
                    <template v-else>
                        <Icon
                            name="LockOpen"
                            size="20px"
                        />
                        <span class="line-through">{{ $t("password") }}</span>
                    </template>
                </div>

                <Deletarium
                    :confirmDeleteButtonText="$t('confirmDeactivation')"
                    :confirmDeletionMessage="$t('confirmDeactivationMessage')"
                    deleteButtonClass="button is-red is-small ml-2"
                    :deleteButtonText="$t('deactivate')"
                    loadingName="deactivateSharing"
                    @delete="deactivateSharing(sharing)"
                />
            </div>
        </transition-group>

        <Pagination
            v-if="sharings.length > 0 && !loadingInProgress.fetchSharingsList"
            class="mt-2"
            :pagination="pagination"
            @pageChange="apiSource.setPage"
        />

        <div
            v-if="sharings.length == 0 && !loadingInProgress.fetchSharingsList"
            class="help-text"
        >
            <div class="help-text-title">
                <Icon
                    class="help-text-icon"
                    name="Share"
                />
                <span>{{ $t("noSharingsYet") }}</span>
            </div>
            <div class="help-text-content">
                {{ $t("sharingHelpText") }}
            </div>
        </div>
    </div>
</MainLayout>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { getSharingTarget } from "@js/generic"
import { getSharingsApiSource } from "@js/apiSource"
import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"
import Pagination from "@components/Pagination"
import SharingsListBulkbar from "./SharingsListBulkbar.vue"

export default {
    name: "SharingAdminApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
        Pagination,
        SharingsListBulkbar,
    },
    data: () => ({
        sharings: [],
        pagination: null,
        apiSource: getSharingsApiSource(),
    }),
    computed: {
        ...mapState("loading", ["loadingInProgress"]),
        ...mapState("bulk", ["bulkActionSelection"]),
    },
    methods: {
        ...mapMutations("bulk", ["toggleForBulkAction"]),
        fetchSharingsList() {
            $httpX({
                name: "fetchSharingsList",
                method: "GET",
                commit: this.$store.commit,
                url: this.apiSource.endpoint,
                params: this.apiSource.queryParamSerializer.params,
            }).then((response) => {
                this.pagination = _.omit(response.data, "objects")
                // This list is append-only, we don't need to check for the append parameter
                this.sharings = response.data.objects
            })
        },
        sharedObjectRepr(sharing) {
            return getSharingTarget(sharing)
        },
        isSelectedForBulkAction(sharing) {
            return this.bulkActionSelection[sharing.id]
        },
        deactivateSharing(sharing) {
            $httpX({
                name: "deactivateSharing",
                method: "POST",
                commit: this.$store.commit,
                url: urls.sharingsDeactivate.format({ token: sharing.token }),
            }).then((response) => {
                this.removeSharingsById([sharing.id])
            })
        },
        removeSharingsById(sharingIds) {
            this.sharings = this.sharings.filter((s) => !sharingIds.includes(s.id))
        },
    },
    watch: {
        "apiSource.url"() {
            this.fetchSharingsList()
        },
    },
    created() {
        this.fetchSharingsList()
    },
    i18n: {
        messages: {
            fr: {
                confirmDeactivation: "Ok, désactiver",
                confirmDeactivationMessage: "Confirmer la désactivation",
                editable: "Modifiable",
                noSharingsYet: "Aucun partage sur ce desk",
                readOnly: "Lecture seule",
                sharingHelpText:
                    "Vous pouvez partager par email des contenus, projets, canaux, filtres, à des contacts sans compte utilisateur.",
            },
            en: {
                confirmDeactivation: "Ok, deactivate",
                confirmDeactivationMessage: "Confirm deactivation",
                editable: "Editable",
                noSharingsYet: "This desk has no sharings",
                readOnly: "Read only",
                sharingHelpText:
                    "You can share by email some contents, projects, channels, filters, to contacts without user account.",
            },
        },
    },
}
</script>

<style lang="scss">
.SharingAdminApp .Deletarium .alert-panel {
    @apply px-1 py-0 m-0 text-sm -mt-1;

    .button {
        @apply text-sm;
    }
}
</style>
