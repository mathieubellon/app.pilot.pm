<template>
<div>
    <OffPanel
        name="NotificationsSettingsPanel"
        key="NotificationsSettingsPanel"
        @opened="onOpen"
    >
        <div slot="offPanelTitle">{{ $t("notificationPreferences") }}</div>
        <div slot="offPanelBody">
            <div class="NotificationsDescription">{{ $t("NotificationsDescription") }}</div>

            <Loadarium name="fetchNotificationFeeds">
                <NotificationPreferencesToggles
                    :notificationPreferences="me.notification_preferences"
                    @toggleApp="toggleUserAppPreference"
                    @toggleEmail="toggleUserEmailPreference"
                />

                <div
                    v-for="notificationFeed in notificationFeeds"
                    class="NotificationSettingsLine"
                    :class="{
                        blink:
                            blinkerNotificationFeed &&
                            notificationFeed.id == blinkerNotificationFeed.id,
                    }"
                >
                    <div
                        v-if="notificationFeed === notificationFeedDeletionRequested"
                        class="danger"
                    >
                        {{ $t("confirmDeletion") }} "{{
                            getNotificationFeedDisplay(notificationFeed)
                        }}" ?
                        <br />
                        <a
                            class="button small alert"
                            @click="confirmNotificationFeedDeletion()"
                        >
                            Ok, {{ $t("confirmDeletion") }}
                        </a>
                        <a
                            class="button small secondary hollow"
                            @click="cancelNotificationFeedDeletion()"
                        >
                            {{ $t("cancel") }}
                        </a>
                    </div>

                    <template v-else>
                        <div class="NotificationSettingsLine__Name">
                            <div>{{ getNotificationFeedDisplay(notificationFeed) }}</div>
                            <div class="NotificationSettingsLine__helptext">
                                {{ $t("headsUp.notificationHelpText") }}
                            </div>
                        </div>

                        <div class="NotificationSettingsLine__actions">
                            <div class="NotificationSettingsLine__toggle">
                                In-app
                                <ToggleButton
                                    :labels="true"
                                    :value="notificationFeed.display_in_app"
                                    @change="toggleFeedAppPreference(notificationFeed)"
                                />
                            </div>
                            <div class="NotificationSettingsLine__toggle">
                                Email
                                <ToggleButton
                                    :labels="true"
                                    :value="notificationFeed.send_email"
                                    @change="toggleFeedEmailPreference(notificationFeed)"
                                />
                            </div>
                            <a
                                v-tooltip="$t('remove')"
                                @click="requestNotificationFeedDeletion(notificationFeed)"
                            >
                                <Icon
                                    class="mt-4"
                                    name="CloseCircle"
                                    size="20px"
                                />
                            </a>
                        </div>
                    </template>
                </div>

                <div class="NotificationSettings__createNew">
                    <a
                        class="button hollow"
                        v-tooltip="$t('newNotificationAreForSavedFilters')"
                        @click="openOffPanel('CreateFeedForSavedFilterPanel')"
                    >
                        <span>{{ $t("createOn.savedFilter") }}</span>
                    </a>
                </div>
            </Loadarium>
        </div>
    </OffPanel>

    <OffPanel
        name="CreateFeedForSavedFilterPanel"
        key="CreateFeedForSavedFilterPanel"
    >
        <div slot="offPanelTitle">{{ $t("newNotificationFeed") }}</div>
        <div slot="offPanelBody">
            <div class="NotificationSettings__createFeedForSavedFilter">
                <div class="alert-panel is-blue">
                    <strong>{{ $t("headsUp.selectSavedFilter") }}</strong>
                    <div>{{ $t("headsUp.notificationHelpText") }}</div>
                </div>

                <VueFuse
                    :defaultAll="true"
                    :keys="['title']"
                    :list="availableSavedFilters"
                    :placeholder="$t('typeToFilter')"
                    :shouldSort="false"
                    :threshold="0.1"
                    @result="onFuseResult"
                />

                <Loading name="fetchSavedFilters" />

                <div
                    v-for="savedFilter in filteredSavedFilters"
                    class="NotificationSettings__savedFilter"
                    @click="requestFeedCreationForSavedFilter(savedFilter)"
                >
                    {{ savedFilter.title }}
                </div>
            </div>
        </div>
    </OffPanel>

    <!--
        <div class="simple-panel NotificationSettings__ActivityStream">
            Suivre l'activité sur : <br /><br />

            <div class="ActivityStream__Param">
                Type d'objet :
                <div class="ActivityStream__ParamSelect">
                    <SelectInput
                        v-model="activityFeedParams.activity_content_type"
                        :choices="contentTypeChoices"
                    />
                </div>
            </div>

            <div class="ActivityStream__Param" v-if="selectedModelSpec && selectedModelSpec.search_api ">
                {{ selectedModelSpec.label }} spécifique :
                <div class="ActivityStream__ParamSelect">
                    <SelectInput
                        v-model="activityFeedParams.activity_object_id"
                        :choices="[]"
                    />
                </div>
            </div>

            <div class="ActivityStream__Param">
                Verb :
                <div class="ActivityStream__ParamSelect">
                    <SelectInput
                        v-model="activityFeedParams.activity_verb"
                        :choices="verbChoices"
                    />
                </div>
            </div>

            <div class="ActivityStream__Param">
                Actor :
                <div class="ActivityStream__ParamSelect">
                    <SelectInput
                        v-model="activityFeedParams.activity_actor"
                        :choices="usersChoices"
                    />
                </div>
            </div>

            <br />
            Vous allez suivre : <strong>{{ formatReadableActivityFeed(activityFeedParams) }}</strong>
            <br />

            <button class="button warning" v-if="isActivityFeedParamsEmpty">
                {{ $t('setParamToSave') }}
            </button>
            <button class="button" @click="createFeedForActivity" v-else>
                {{ $t('createFeed') }}
            </button>
        </div>
        -->
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { FEED_TYPE_ITEM_SAVED_FILTER } from "@/store/modules/NotificationSettingsStore"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"

import { Fragment } from "vue-fragment"
import { ToggleButton } from "vue-js-toggle-button"

import NotificationPreferencesToggles from "@views/notifications/settings/NotificationPreferencesToggles"

const EMPTY_ACTIVITY_PARAMS = {
    activity_actor: null,
    activity_content_type: null,
    activity_object_id: null,
    activity_verb: "",
}

export default {
    name: "NotificationsSettingsPanel",
    mixins: [PilotMixin],
    components: {
        Fragment,
        ToggleButton,
        NotificationPreferencesToggles,
    },
    data: () => ({
        notificationFeedDeletionRequested: null,
        filteredSavedFilters: [],
        activityFeedParams: _.clone(EMPTY_ACTIVITY_PARAMS),
    }),
    computed: {
        ...mapState("users", ["me"]),
        ...mapState("savedFilter", ["savedFilters"]),
        ...mapState("notificationSettings", ["notificationFeeds", "blinkerNotificationFeed"]),
        ...mapGetters("choices", ["usersChoices", "getChoiceDisplay"]),
        availableSavedFilters() {
            let followedSavedFilters = this.notificationFeeds
                .filter((nf) => nf.feed_type == FEED_TYPE_ITEM_SAVED_FILTER)
                .map((nf) => nf.saved_filter)
            // Sort on on icase title
            return sortByAlphaString(
                _.differenceBy(this.savedFilters, followedSavedFilters, "id"),
                (savedFilter) => savedFilter.title,
            )
        },
        /*verbChoices(){
            let spec = notificationCenterContext.activityFeedSpec
            let verbs
            if( this.selectedModelSpec && this.selectedModelSpec.verbs ){
                verbs = [...spec.common_verbs, ...this.selectedModelSpec.verbs]
            }
            else{
                verbs = [...spec.common_verbs]
            }
            return verbs.map(verb => ({
                id: verb,
                text: spec.verb_choices[verb]
            }))
        }*/
    },
    methods: {
        ...mapActions("users", ["partialUpdateUser"]),
        ...mapActions("savedFilter", ["fetchSavedFilters"]),
        ...mapActions("notificationSettings", [
            "fetchNotificationFeeds",
            "createFeedForSavedFilter",
            "deleteNotificationFeed",
            "toggleFeedAppPreference",
            "toggleFeedEmailPreference",
            "blinkNotificationFeed",
        ]),
        onOpen() {
            // Do fetch at the first open only
            if (_.isEmpty(this.notificationFeeds)) {
                this.fetchNotificationFeeds()
            }

            this.fetchSavedFilters()
        },
        toggleUserAppPreference(ptriggerElementName) {
            let notification_preferences = this.me.notification_preferences
            notification_preferences[ptriggerElementName].app = !Boolean(
                notification_preferences[ptriggerElementName].app,
            )
            this.partialUpdateUser({ notification_preferences })
        },
        toggleUserEmailPreference(ptriggerElementName) {
            let notification_preferences = this.me.notification_preferences
            notification_preferences[ptriggerElementName].email = !Boolean(
                notification_preferences[ptriggerElementName].email,
            )
            this.partialUpdateUser({ notification_preferences })
        },
        /*createFeedForActivity(){
            let data = _.assign({feed_type: FEED_TYPE_ACTIVITY_STREAM}, this.activityFeedParams)
            $httpX({
                name: 'createFeedForSavedFilter',
                commit: this.$store.commit,
                url: urls.notificationFeeds,
                method: "POST",
                data: data
            })
            .then(response => {
                this.notificationFeeds.unshift(response.data)
                this.activityFeedParams = _.clone(EMPTY_ACTIVITY_PARAMS)
            })
        },*/
        requestFeedCreationForSavedFilter(savedFilter) {
            this.createFeedForSavedFilter(savedFilter).then(() => {
                this.blinkNotificationFeed(this.notificationFeeds[0])
                this.closeOffPanel("CreateFeedForSavedFilterPanel")
                this.openOffPanel("NotificationsSettingsPanel")
            })
        },
        requestNotificationFeedDeletion(notificationFeed) {
            this.notificationFeedDeletionRequested = notificationFeed
        },
        confirmNotificationFeedDeletion() {
            this.deleteNotificationFeed(this.notificationFeedDeletionRequested).then((response) => {
                this.notificationFeedDeletionRequested = null
            })
        },
        cancelNotificationFeedDeletion() {
            this.notificationFeedDeletionRequested = null
        },
        getNotificationFeedDisplay(notificationFeed) {
            if (notificationFeed.feed_type == "item_saved_filter")
                return (
                    this.$t("forTheSavedFilter") + ' "' + notificationFeed.saved_filter.title + '"'
                )
            else return this.formatReadableActivityFeed(notificationFeed)
        },
        getModelSpec(contentTypeId) {
            return _.find(notificationCenterContext.activityFeedSpec.models, (modelSpec) => {
                return "" + modelSpec.content_type_id == "" + contentTypeId
            })
        },
        formatReadableActivityFeed(notificationFeed) {
            let output = ""

            if (notificationFeed.activity_verb) {
                let verbDisplay =
                    notificationCenterContext.activityFeedSpec.verb_choices[
                        notificationFeed.activity_verb
                    ]
                output += "Les activités de type " + verbDisplay
            } else {
                output += "Toutes les activités"
            }

            if (notificationFeed.activity_actor) {
                let username = this.getChoiceDisplay(
                    "usersChoices",
                    notificationFeed.activity_actor,
                )
                output += " par l'utilisateur " + username
            } else {
                output += " par n'importe quel user"
            }

            if (notificationFeed.activity_content_type) {
                let modelSpec = this.getModelSpec(notificationFeed.activity_content_type)
                if (!notificationFeed.activity_object_id) {
                    output += ' sur tous les objets "' + modelSpec.label + '"'
                } else {
                    output +=
                        " sur le " + modelSpec.label + " #" + notificationFeed.activity_object_id
                }
            } else {
                output += " sur tous les objets"
            }

            return output
        },
        onFuseResult(filteredSavedFilters) {
            // Sort on on icase title
            this.filteredSavedFilters = filteredSavedFilters
        },
    },
    i18n: {
        messages: {
            fr: {
                confirmDeletion: "Ne plus suivre",
                createNotificationFeed: "Créer une nouvelle notification",
                createOn: {
                    savedFilter: "Nouvelle notification",
                },
                forTheSavedFilter: "Filtre",
                headsUp: {
                    selectSavedFilter: "Sélectionnez un de vos filtres ci-dessous",
                    notificationHelpText:
                        "Vous serez notifié quand un contenu entre dans la liste, quitte la liste ou est modifié",
                },
                newNotificationFeed: "Nouvelle Notification",
                notificationPreferences: "Préférences de notification",
                NotificationsDescription:
                    'Chaque notification peut être signalée "in-app" sous l\'icône représentée par une cloche rouge et/ou par email',
                newNotificationAreForSavedFilters:
                    "Pour le moment vous pouvez être notifié de l'activité de vos filtres sauvegardés uniquement. <br> D'autres possibilités de notifications seront ajoutées à la demande.",
            },
            en: {
                confirmDeletion: "Stop following",
                createNotificationFeed: "Create a new notification",
                createOn: {
                    savedFilter: "Create a notification",
                },
                forTheSavedFilter: "Filter",
                headsUp: {
                    selectSavedFilter: "Select one of your filters below",
                    notificationHelpText:
                        "You will be notified when a content enters the list, exits the list or is changed",
                },
                newNotificationFeed: "New Notification",
                notificationPreferences: "Notification preferences",
                NotificationsDescription:
                    'Each notification can be indicated "in-app" under the icon represented by a red bell and/or by email',
                newNotificationAreForSavedFilters:
                    "For the moment you can be notified of the activity of your saved filters only. <br> Other notifications options will be added on request.",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

@-webkit-keyframes blinker {
    50% {
        color: $blue;
        background-color: $gray-lighter;
    }
}

.NotificationsDescription {
    margin-top: -1.6em;
    margin-bottom: 2.4em;
}

.NotificationSettings__savedFilter {
    padding: 0.5em;
    margin-bottom: 0.5em;
    border-radius: 3px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #f5f5f5;
}
.NotificationSettings__savedFilter:hover {
    background-color: #607d8b;
    color: #fff;
    cursor: pointer;
}

.NotificationSettings__createNew {
    display: flex;
    flex-direction: column;

    margin-top: 4em;
}
</style>
