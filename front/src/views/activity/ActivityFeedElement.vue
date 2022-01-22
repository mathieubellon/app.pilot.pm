<template>
<div class="ActivityFeedElement">
    <!-- This transition handle comment deletion -->
    <transition
        enter-active-class="animated fadeIn"
        leave-active-class="animated fadeOut"
        mode="out-in"
    >
        <div
            v-if="activity.is_comment"
            class="flex"
            key="comment"
        >
            <div class="flex flex-shrink-0 mr-2">
                <UserDisplay
                    avatarSize="25px"
                    :user="activity.user"
                    :withAvatar="true"
                    :withUsername="false"
                />
            </div>
            <div class="flex flex-col flex-grow text-gray-700 break w-full">
                <div class="text-xs font-medium flex items-center">
                    <UserDisplay
                        :user="activity.user"
                        :withAvatar="false"
                    />
                    &nbsp;&#8226;&nbsp;
                    <div>
                        {{ activity.created_at | dateTimeFormatShort }}
                    </div>
                    <div v-if="comment.data && comment.data.version">
                        &nbsp;&#8226;&nbsp;
                        {{ comment.data.version }}
                    </div>
                </div>

                <transition
                    enter-active-class="animated fadeIn"
                    leave-active-class="animated fadeOut"
                    mode="out-in"
                >
                    <div
                        v-if="activity == activityCommentInEdition"
                        class="border border-gray-300 rounded text-base bg-white w-full pt-0 flex-grow"
                        key="commentEdition"
                    >
                        <CommentBox
                            v-model="editedComment"
                            class="flex-grow w-full mb-4"
                            :autoFocus="true"
                            :contentType="contentType"
                            :inactiveMentionGroups="inactiveMentionGroups"
                        />
                        <SmartButtonSpinner
                            class="button is-xsmall is-blue mt-0 ml-4 mb-2"
                            name="editComment"
                            @click="validateCommentEdition"
                        >
                            {{ $t("edit") }}
                        </SmartButtonSpinner>
                        <button
                            class="button is-xsmall mt-0 ml-2 mb-2"
                            @click="endCommentEdition"
                        >
                            {{ $t("cancel") }}
                        </button>
                    </div>

                    <div
                        v-else-if="activity == activityCommentInDeletion"
                        key="commentDeletion"
                    >
                        <SmartButtonSpinner
                            class="button is-red"
                            name="deleteComment"
                            @click="confirmCommentDeletion"
                        >
                            {{ $t("confirmDeletion") }}
                        </SmartButtonSpinner>
                        <button
                            class="button"
                            @click="endCommentDeletion"
                        >
                            {{ $t("cancel") }}
                        </button>
                    </div>

                    <!--
                    Please, don't use .bg-grey-50 from tailwindcss, because it would
                    take precedence over our color_change animation
                    because .bg-white has the !important flag.
                    -->
                    <div
                        v-else-if="isDeletedComment"
                        class="p-4 text-gray-500 rounded border border-gray-200 ActivityFeed__Comment deleted"
                        :class="'comment-' + comment.id"
                        key="deletedComment"
                    >
                        {{ $t("commentDeleted") }}
                    </div>

                    <!--
                    Please, don't use .bg-white from tailwindcss, because it would
                    take precedence over our color_change animation
                    because .bg-white has the !important flag.
                    -->
                    <div
                        v-else
                        class="ActivityFeed__Comment p-4 rounded border border-gray-200"
                        :class="'comment-' + comment.id"
                        key="commentDisplay"
                    >
                        <CommentDisplay :comment="comment.comment_content" />
                        <div
                            v-if="comment.edition_date"
                            class="text-sm text-right text-gray-600"
                        >
                            {{ $t("editedOn") }} {{ comment.edition_date | dateFormat("LL") }}
                        </div>
                    </div>
                </transition>

                <div
                    v-if="activity.user.id == users.me.id"
                    v-show="
                        !activityCommentInEdition && !activityCommentInDeletion && !isDeletedComment
                    "
                >
                    <a
                        class="actionlink text-xs font-semibold underline text-gray-600"
                        @click.prevent="startCommentEdition"
                    >
                        {{ $t("edit") }}
                    </a>
                    <a
                        class="actionlink text-xs font-semibold underline text-gray-600 ml-2"
                        @click.prevent="requestCommentDeletionConfirmation"
                    >
                        {{ $t("delete") }}
                    </a>
                </div>
            </div>
        </div>

        <div
            v-else
            class="flex text-sm font-medium rounded text-gray-800"
            key="activity"
        >
            <div class="flex flex-shrink-0 mr-2">
                <UserDisplay
                    v-if="activity.user"
                    :avatarSize="'25px'"
                    :user="activity.user"
                    :withAvatar="true"
                    :withUsername="false"
                />
            </div>
            <div class="ActivityFeed__Action__Content text-teal-900 w-full">
                <div class="text-xs flex items-center">
                    <div class="text-gray-900 font-bold text-sm mb-1">
                        <UserDisplay
                            v-if="activity.user"
                            :user="activity.user"
                            :withAvatar="false"
                        />
                        <span v-else-if="activity.actor_display">{{ activity.actor_display }}</span>
                    </div>
                    &nbsp;&#8226;&nbsp;
                    <div class="text-xs">{{ activity.created_at | dateTimeFormatShort }}</div>
                </div>
                <div class="ActivityFeed__Action__What flex items-center">
                    <span
                        class="flex items-center flex-shrink-0 bg-teal-100 text-teal-900 text-xs text-white font-base rounded-full mr-2"
                    >
                        <Icon
                            class="border-2 border-white rounded-full bg-white fill-current text-teal-500"
                            name="Activity"
                            size="16px"
                        />
                        <span class="px-2">{{ activity.verb_display }}</span>
                    </span>

                    <!-- Action object display ( only for the instance activity stream ) -->
                    <template v-if="actionObjectRepr && isInstanceActivityFeed">
                        {{ actionObjectRepr }}
                    </template>
                    <!-- Linked object display ( only for the main activity stream ) -->
                    <template v-if="targetRepr && !isInstanceActivityFeed">
                        <SmartLink
                            v-if="activityUrl"
                            :to="activityUrl"
                        >
                            {{ targetRepr }}
                        </SmartLink>
                        <span v-else>
                            {{ targetRepr }}
                        </span>
                        <!-- <span v-if="activity.action_object && actionObjectRepr"></span> -->
                    </template>

                    <a
                        v-if="canShowDiffDetails"
                        class="underline text-xs font-medium text-teal-900 ml-2"
                        @click="toggleActivityDetails"
                    >
                        {{ $t("details") }}
                    </a>
                </div>
                <transition
                    enter-active-class="animated fadeIn"
                    leave-active-class="animated fadeOut"
                >
                    <div v-show="isDetailsOpen">
                        <ActivityFieldDiff
                            v-for="(fieldDiff, index) in activity.diff"
                            :activity="activity"
                            :fieldDiff="fieldDiff"
                            :key="index"
                        />
                    </div>
                </transition>
            </div>
        </div>
    </transition>
</div>
</template>

<script>
import _ from "lodash"
import PilotMixin from "@components/PilotMixin"
import { getGLORepr } from "@js/generic"
import ActivityFeedStoreMapper from "./ActivityFeedStoreMapper"

import CommentBox from "@components/CommentBox"
import CommentDisplay from "@components/CommentDisplay"
import ActivityFieldDiff from "./ActivityFieldDiff"

const ActivityVerbs = {
    VERB_ACCEPTED_IDEA: "accepted_idea",
    VERB_ASSET_LINKED: "asset_linked",
    VERB_ASSET_UNLINKED: "asset_unlinked",
    VERB_CANCELLED_REJECTION: "cancelled_rejection",
    VERB_CLOSED: "closed",
    VERB_COMMENTED: "commented",
    VERB_COPIED: "copied",
    VERB_CREATED: "created",
    VERB_DELETED: "deleted",
    VERB_FEEDBACK_APPROVED: "feedback_approved",
    VERB_FEEDBACK_REJECTED: "feedback_rejected",
    VERB_HIDDEN: "hidden",
    VERB_JOINED_TEAM: "joined_the_team",
    VERB_PUT_IN_TRASH: "put_in_trash",
    VERB_REJECTED_IDEA: "rejected_idea",
    VERB_REOPENED: "reopened",
    VERB_RESTORED: "restored",
    VERB_RESTORED_FROM_TRASH: "restored_from_trash",
    VERB_REVOKED: "revoked",
    VERB_SHARED: "shared",
    VERB_STARTED_EDIT_SESSION: "started_edit_session",
    VERB_TASK_CREATED: "task_created",
    VERB_TASK_DELETED: "task_deleted",
    VERB_TASK_DONE: "task_done",
    VERB_TASK_UPDATED: "task_updated",
    VERB_UPDATED: "updated",
    VERB_UPDATED_WORKFLOW: "updated_workflow",
    VERB_CREATE_MAJOR_VERSION: "create_major_version",
}

export default {
    name: "ActivityFeedElement",
    mixins: [PilotMixin, ActivityFeedStoreMapper],
    components: {
        CommentBox,
        CommentDisplay,
        ActivityFieldDiff,
    },
    props: {
        activity: Object,
    },
    data: () => ({
        isDetailsOpen: false,

        editedComment: null,
        activityCommentInEdition: null,
        activityCommentInDeletion: null,
    }),
    inject: ["inactiveMentionGroups", "isInstanceActivityFeed"],
    computed: {
        users() {
            return this.$store.state.users
        },
        comment() {
            return this.activity.is_comment ? this.activity.action_object.details : null
        },
        isDeletedComment() {
            return this.activity.is_comment && this.comment.is_deleted
        },
        canShowDiffDetails() {
            return (
                this.activity.diff &&
                this.activity.diff.length > 0 &&
                // Special case for item activity
                !(this.isInstanceActivityFeed && this.activity.diff[0].field_name == "json_content")
            )
        },
        /**
         * Returns the url where this activity took place.
         * Give priority to the action object if it has an url, else go to the target url.
         * This allow to be more specific for those action object that implements a specific action
         * ( show task, show comment, show sharing modal... )
         */
        activityUrl() {
            let actionObjectUrl = _.get(this.activity, "action_object.details.url")
            if (actionObjectUrl) {
                return actionObjectUrl
            } else {
                return _.get(this.activity, "target.details.url")
            }
        },
        targetRepr() {
            return getGLORepr(this.activity.target)
        },
        actionObjectRepr() {
            return getGLORepr(this.activity.action_object)
        },
    },
    methods: {
        toggleActivityDetails() {
            this.isDetailsOpen = !this.isDetailsOpen
        },
        startCommentEdition() {
            this.editedComment = this.comment.comment_content
            this.activityCommentInEdition = this.activity
        },
        validateCommentEdition() {
            this.editComment({
                activityId: this.activityCommentInEdition.id,
                commentContent: this.editedComment,
            }).then(this.endCommentEdition)
        },
        endCommentEdition() {
            this.activityCommentInEdition = null
            this.activityCommentInEdition = null
        },
        requestCommentDeletionConfirmation() {
            this.activityCommentInDeletion = this.activity
        },
        confirmCommentDeletion() {
            this.deleteComment({
                activityId: this.activityCommentInDeletion.id,
            }).then(this.endCommentDeletion)
        },
        endCommentDeletion() {
            this.activityCommentInDeletion = null
        },
    },
    i18n: {
        messages: {
            fr: {
                commentDeleted: "Commentaire supprimé par l'auteur",
                editedOn: "Edité le",
                noActivity: "Pas d'activités à afficher",
                seeActivity: "Afficher les activités",
            },
            en: {
                commentDeleted: "∅ Comment deleted by the author",
                editedOn: "Edited on",
                noActivity: "No activity to display",
                seeActivity: "Show activities",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.ActivityFeedElement {
    @apply mb-6;
}
.ActivityFeed__Comment {
    @keyframes color_change {
        from {
            background-color: #fff;
        }
        to {
            background-color: #9fe6fe;
        }
    }

    // Please, don't use .bg-white from tailwindcss, because it would
    // take precedence over our color_change animation
    // because .bg-white has the !important flag.
    background: white;

    &.twinkle {
        animation: color_change 0.4s 8 alternate;
    }

    &.deleted {
        // Please, don't use .bg-grey-50 from tailwindcss, because it would
        // take precedence over our color_change animation
        // because .bg-white has the !important flag.
        background: $grey050;
    }
}
</style>
