<template>
<div class="AnnotationElement">
    <div
        v-show="annotation.mainComment.content"
        class="AnnotationElement__header"
    >
        <a
            class="AnnotationElement__close"
            @click="annotationManager.deselectAnnotations()"
        >
            {{ $t("close") }}
        </a>
        <div
            v-show="canAnnotate"
            class="AnnotationElement__resolve"
            @click="resolveAnnotationRequested = true"
        >
            <input
                :id="'resolveAnnotation' + annotation.id"
                type="checkbox"
                :value="annotation.resolved"
            />
            <span :for="'resolveAnnotation' + annotation.id">{{ $t("resolved") }}</span>
        </div>
        <div
            v-show="resolveAnnotationRequested"
            class="AnnotationElement__confirmResolve"
        >
            {{ $t("markAsResolvedWithWarning") }}:
            <div>
                <a @click="annotationManager.resolveAnnotation(annotation)">
                    {{ $t("ok") }}
                </a>
                <a @click="resolveAnnotationRequested = false">
                    {{ $t("cancel") }}
                </a>
            </div>
        </div>
    </div>

    <!-- for TextAnnotations only -->
    <div
        v-if="annotation.selectedText"
        class="AnnotationElement__selectedText"
    >
        {{ annotation.selectedText }}
    </div>

    <div class="AnnotationElement__comments">
        <div
            v-if="annotation.mainComment.content"
            class="AnnotationElement__comment"
        >
            <div class="AnnotationElement__user">
                <img
                    v-if="annotation.mainComment.user.avatar"
                    class="AnnotationElement__avatar"
                    :src="annotation.mainComment.user.avatar"
                />
            </div>

            <div class="AnnotationElement__commentActions">
                <span
                    v-show="
                        canAnnotate &&
                        annotationManager.ownComment(annotation.mainComment) &&
                        annotationManager.editedComment != annotation.mainComment
                    "
                >
                    <a
                        class="edit"
                        @click="startCommentEdition(annotation.mainComment)"
                    >
                        {{ $t("edit") }}
                    </a>
                </span>
                <div class="AnnotationElement__user">
                    <UserDisplay :user="annotation.mainComment.user" />
                </div>
                <div class="AnnotationElement__timeAgo">
                    {{ annotation.mainComment.date | timeAgo }}
                </div>
            </div>

            <div
                v-show="annotationManager.editedComment != annotation.mainComment"
                class="AnnotationElement__commentContent"
            >
                <CommentDisplay :comment="annotation.mainComment.content" />
            </div>
            <!-- This is to EDIT the MAIN COMMENT -->
            <div v-if="canAnnotate && annotationManager.editedComment == annotation.mainComment">
                <CommentBox
                    v-model="commentContent"
                    :autoFocus="true"
                    :contentType="contentTypes.Item"
                    :inactiveMentionGroups="inactiveMentionGroups"
                />
                <a
                    class="save"
                    @click="addOrEditAnnotationComment()"
                >
                    {{ $t("save") }}
                </a>
                <a
                    class="cancel"
                    @click="endCommentEdition()"
                >
                    {{ $t("cancel") }}
                </a>
            </div>
        </div>

        <div
            v-for="(comment, index) in annotation.comments"
            class="comment"
        >
            <div class="AnnotationElement__user">
                <img
                    v-if="comment.user.avatar"
                    class="AnnotationElement__avatar"
                    :src="comment.user.avatar"
                />
            </div>

            <div class="AnnotationElement__commentActions">
                <span
                    v-show="
                        canAnnotate &&
                        annotationManager.ownComment(comment) &&
                        annotationManager.editedComment != comment
                    "
                >
                    <a @click="annotationManager.removeAnnotationComment(annotation, index)">
                        {{ $t("delete") }}
                    </a>
                    <a @click="startCommentEdition(comment)">
                        {{ $t("edit") }}
                    </a>
                </span>
                <div class="AnnotationElement__user">
                    <UserDisplay :user="comment.user" />
                </div>
                <div class="AnnotationElement__timeAgo">{{ comment.date | timeAgo }}</div>
            </div>

            <div
                v-show="annotationManager.editedComment != comment"
                class="AnnotationElement__commentContent"
            >
                <CommentDisplay :comment="comment.content" />
            </div>
            <div v-if="canAnnotate && annotationManager.editedComment == comment">
                <!-- This is to EDIT a SECONDARY COMMENT -->
                <CommentBox
                    v-model="commentContent"
                    :autoFocus="true"
                    :contentType="contentTypes.Item"
                    :inactiveMentionGroups="inactiveMentionGroups"
                />
                <a @click="addOrEditAnnotationComment()">
                    {{ $t("save") }}
                </a>
                <a @click="endCommentEdition()">
                    {{ $t("cancel") }}
                </a>
            </div>
        </div>
    </div>
    <div
        v-if="
            annotationManager.user &&
            canAnnotate &&
            (!annotationManager.editedComment || annotationManager.annotationInCreation)
        "
        class="AnnotationElement__newComment"
    >
        <img
            v-if="annotationManager.user.avatar"
            class="AnnotationElement__avatar"
            :src="annotationManager.user.avatar"
        />

        <!-- This is to CREATE a SECONDARY COMMENT -->
        <div v-if="hasAMainComment && !isCreateSecondaryCommentEditorVisible">
            <textarea
                class="h-12"
                :placeholder="$t('addComment')"
                @click="startSecondaryCommentCreation"
            />
        </div>

        <div v-else>
            <CommentBox
                v-model="commentContent"
                :autoFocus="true"
                :contentType="contentTypes.Item"
                :inactiveMentionGroups="inactiveMentionGroups"
            />

            <a
                class="save"
                @click="addOrEditAnnotationComment()"
            >
                {{ $t("save") }}
            </a>
            <a
                class="cancel"
                @click="endCommentEdition()"
            >
                {{ $t("cancel") }}
            </a>
        </div>
    </div>
</div>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import PilotMixin from "@components/PilotMixin"

import CommentBox from "@components/CommentBox"
import CommentDisplay from "@components/CommentDisplay"

export default {
    name: "AnnotationElement",
    mixins: [PilotMixin],
    components: {
        CommentBox,
        CommentDisplay,
    },
    props: {
        annotation: Object,
        annotationManager: Object,
        readOnly: Boolean,
    },
    data: () => ({
        resolveAnnotationRequested: false,
        commentContent: null,
        isCreateSecondaryCommentEditorVisible: false,
    }),
    computed: {
        ...mapGetters("itemDetail", ["inactiveMentionGroups"]),
        canAnnotate() {
            return !this.readOnly
        },
        hasAMainComment() {
            return this.annotation.mainComment.content
        },
    },
    methods: {
        startSecondaryCommentCreation() {
            this.isCreateSecondaryCommentEditorVisible = true
        },
        startCommentEdition(comment) {
            this.commentContent = comment.content
            this.annotationManager.startCommentEdition(comment)
        },
        addOrEditAnnotationComment() {
            this.annotationManager.addOrEditAnnotationComment(this.annotation, this.commentContent)
            this.endCommentEdition()
        },
        endCommentEdition() {
            this.annotationManager.cancelCommentEdition()
            this.commentContent = null
            this.isCreateSecondaryCommentEditorVisible = false
        },
    },
    i18n: {
        messages: {
            fr: {
                resolved: "Résolue",
                markAsResolvedWithWarning:
                    "Vous allez marquer cette annotation comme résolue (elle sera masquée)",
            },
            en: {
                resolved: "Resolved",
                markAsResolvedWithWarning:
                    "You will mark this annotation as resolved (it will be hidden)",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
@import "~@sass/business/items_vars.scss";

$sizeAvatar: 26px;

.AnnotationElement {
    display: block;
    width: 100%;
    border: 1px solid #cecece;
    margin-bottom: 10px;
    background: #fff;
    -webkit-border-radius: 3px;
    border-radius: 3px;
    box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
    // Below Popper (100) and Offpanel (90)
    z-index: 30;

    a {
        font-size: 0.8em;
        cursor: pointer;
        text-decoration: none;
    }
}

.AnnotationElement__close {
    padding: 6px;
    font-size: 0.8em;
    cursor: pointer;
    float: right;
    color: $grey600;
    text-decoration: none;
}

.AnnotationElement__resolve {
    padding: 6px;
    border-bottom: 1px solid $gray-lighter;
    font-size: 0.8em;
    color: $grey600;

    input {
        margin: 0;
    }
    span {
        cursor: pointer;
        &:hover {
            @apply text-blue-700;
        }
    }
}

.AnnotationElement__confirmResolve {
    background-color: #f2f6fa;
    padding: 5px;
    margin: 5px;

    a {
        background: #fff;
        padding: 3px;
        margin-right: 3px;
        margin-top: 3px;
        font-size: 1.1em;
    }
}

.AnnotationElement__selectedText {
    border-bottom: 1px solid #cecece;
    padding: 10px;
    color: $grey500;
    font-style: italic;
    font-size: 0.9em;
    quotes: "«" "»";
    &::before {
        content: open-quote;
    }
    &::after {
        content: close-quote;
    }

    /* handle ellipsis */
    max-height: 45px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    &:hover {
        max-height: none;
        white-space: normal;
    }
}

.AnnotationElement__avatar {
    width: $sizeAvatar;
    height: auto;
    -webkit-border-radius: 50%;
    border-radius: 50%;
}

.AnnotationElement__newComment {
    padding: 10px;
    background-color: #f6f9fc;
    border-top: 1px solid #ececec;
    a:first-of-type {
        margin-left: $sizeAvatar + 7px;
    }

    textarea,
    textarea:focus {
        border: none;
        background: none;
        box-shadow: none;
        outline: none !important;
        //min-height: $sizeAvatar !important;
        margin-bottom: 0px;
        width: calc(100% - #{$sizeAvatar} - 5px);
        vertical-align: top;
        display: inline-block;
        padding: 3px 0 0 3px;
    }
}

.AnnotationElement__comments {
    padding: 10px;
    .buttons {
        text-align: center;
    }

    textarea {
        border: none;
        background: $gray-lighter;
        width: 100% !important;
        margin-top: 5px;
        padding: 8px;
    }
}

.AnnotationElement__comment {
    padding: 5px;
}

.AnnotationElement__user {
    display: inline-block;
    vertical-align: top;
}

.AnnotationElement__timeAgo {
    font-size: 0.8em;
    color: $grey500;
}

.AnnotationElement__commentActions {
    display: inline-block;
    margin: 2px 0 0 2px;

    .AnnotationElement__user {
        font-size: 0.9em;
    }

    a {
        display: inline-block;
        margin-left: 5px;
        cursor: pointer;
        float: right;
    }
}

.AnnotationElement__commentContent {
    display: block;
    font-size: 1em;
    word-wrap: break-word;
    width: 100%;
    padding-left: $sizeAvatar + 5px;
}
</style>
