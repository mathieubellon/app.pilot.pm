<template>
<div class="ActivityFeed">
    <div
        v-if="isInstanceActivityFeed"
        class="ActivityFeed__send"
    >
        <div class="flex flex-shrink-0 mr-2">
            <UserDisplay
                avatarSize="25px"
                :user="users.me"
                :withAvatar="true"
                :withUsername="false"
            />
        </div>

        <div class="RichTextCommentContainer flex-grow">
            <transition
                enter-active-class="animated animated-150 fadeIn"
                leave-active-class="animated animated-150 fadeOut"
                mode="out-in"
            >
                <input
                    v-if="!isCreateCommentEditorVisible"
                    class="w-full rounded px-2 h-10"
                    :placeholder="$t('addComment')"
                    @click="startCommentCreation"
                    @focus="startCommentCreation"
                />
                <div v-else>
                    <CommentBox
                        v-model="newComment"
                        class="mb-3"
                        ref="createCommentEditor"
                        :autoFocus="true"
                        :contentType="contentType"
                        :inactiveMentionGroups="inactiveMentionGroups"
                    />
                    <div class="flex">
                        <SmartButtonSpinner
                            class="button is-xsmall is-blue mt-0 ml-4 mb-2"
                            name="createComment"
                            :timeout="0"
                            @click="validateCommentCreation"
                        >
                            {{ $t("send") }}
                        </SmartButtonSpinner>
                        <button
                            class="button is-xsmall mt-0 ml-2 mb-2"
                            @click="endCommentCreation"
                        >
                            {{ $t("cancel") }}
                        </button>
                    </div>
                </div>
            </transition>
        </div>
    </div>
    <div
        v-if="isInstanceActivityFeed"
        class="flex justify-between"
    >
        <!-- We need an empty span when not loading, to push to the right the toggleActivitiesVisibility  -->
        <Loadarium name="fetchActivities"><span /></Loadarium>

        <a
            v-if="showActivites"
            class="button bg-gray-200 is-small"
            @click="toggleActivitiesVisibility"
        >
            {{ $t(areActionActivitiesVisible ? "hideActivity" : "showActivity") }}
        </a>
    </div>

    <div
        v-if="isInstanceActivityFeed && isCommentListEmpty"
        class="help-text max-w-none mt-0"
    >
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="Comment"
            />
            <span>{{ $t("noComments") }}</span>
        </div>
        <div class="help-text-content">{{ $t("explainComments") }}</div>
    </div>

    <div class="ActivityFeed__ActivityList">
        <transition-group
            enter-active-class="animated fadeInDown"
            leave-active-class="animated fadeOut"
        >
            <div
                v-for="activity in activities"
                class="ActivityFeed__ActivityListElement"
                :id="'activity-' + activity.id"
                :key="activity.id"
            >
                <ActivityFeedElement
                    v-if="activity.is_comment || areActionActivitiesVisible"
                    :activity="activity"
                    :namespace="namespace"
                />
            </div>
        </transition-group>

        <Loading
            class="middle"
            name="appendActivities"
        />

        <button
            v-if="pagination && !isActivityListEmpty"
            class="button load-more"
            :disabled="pagination.next === null"
            @click.prevent="fetchActivities(true)"
        >
            <div v-if="pagination.next">
                {{ $t("loadPage") }} {{ pagination.next }} / {{ pagination.num_pages }}
            </div>
            <div v-else>{{ $t("noMoreResults") }}</div>
        </button>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import { waitUntil } from "@js/utils"
import PilotMixin from "@components/PilotMixin"
import ActivityFeedStoreMapper from "./ActivityFeedStoreMapper"

import CommentBox from "@components/CommentBox"
import ActivityFeedElement from "./ActivityFeedElement"

export default {
    name: "ActivityFeed",
    mixins: [PilotMixin, ActivityFeedStoreMapper],
    components: {
        CommentBox,
        ActivityFeedElement,
    },
    props: {
        inactiveMentionGroups: Object,
        showActivites: {
            type: Boolean,
            default: true,
        },
    },
    data: () => ({
        // Should we display the actions activities ?
        areActionActivitiesVisible: false,
        newComment: null,
        isCreateCommentEditorVisible: false,
    }),
    provide() {
        return {
            inactiveMentionGroups: this.inactiveMentionGroups,
            isInstanceActivityFeed: this.isInstanceActivityFeed,
        }
    },
    computed: {
        // Are we in the context of the dashboard, or a specific instance ?
        isInstanceActivityFeed() {
            return Boolean(this.contentType && this.objectId)
        },
        users() {
            return this.$store.state.users
        },
        isCommentListEmpty() {
            return _.filter(this.activities, { is_comment: true }).length == 0
        },
    },
    methods: {
        toggleActivitiesVisibility() {
            this.areActionActivitiesVisible = !this.areActionActivitiesVisible
            if (this.areActionActivitiesVisible) {
                this.fetchActivities()
            }
        },
        startCommentCreation() {
            this.isCreateCommentEditorVisible = true

            waitUntil(
                () => this.$refs.createCommentEditor && this.$refs.createCommentEditor.editor,
                () => this.$refs.createCommentEditor.editor.focus(),
            )
        },
        validateCommentCreation() {
            this.createComment(this.newComment).then(this.endCommentCreation)
        },
        endCommentCreation() {
            this.isCreateCommentEditorVisible = false
            setTimeout(() => {
                this.newComment = null
            }, 500)
        },
    },
    created() {
        this.areActionActivitiesVisible = this.showActivites && !this.isInstanceActivityFeed
    },
    i18n: {
        messages: {
            fr: {
                explainComments:
                    "Les commentaires sont très utiles pour partager l'information sur un contenu ou interpeller d'autres membres de l'équipe (tapez '@' dans le champ au dessus). Lancez vous !",
                hideActivity: "Masquer les activités",
                noActivity: "Pas d'activités à afficher",
                noComments: "Aucun commentaire !",
                send: "Envoyer",
                showActivity: "Voir l'activité",
            },
            en: {
                explainComments:
                    "Comments are very useful to share some informations on a content or reach out to another member of the team ( type '@' in the input field ). Give it a try !",
                hideActivity: "Hide activities",
                noActivity: "No activity to display",
                noComments: "No comment !",
                send: "Send",
                showActivity: "Show activity",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
.ActivityFeed {
    @apply flex flex-col flex-grow min-h-0;
}
.ActivityFeed__send {
    @apply flex py-4 flex-shrink-0 items-center;
}
.ActivityFeed__ActivityList {
    @apply flex flex-col flex-grow overflow-y-auto min-h-0 pt-5;
}
</style>
