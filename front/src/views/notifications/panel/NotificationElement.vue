<template>
<div
    class="Notification"
    :class="{ isRead: notification.is_read }"
    @mouseleave="showActions = false"
    @mouseover="showActions = true"
>
    <div class="Notification__Icon flex-col">
        <UserAvatar
            class="rounded-full h-6 w-6"
            size="30px"
            :user="notification.send_by"
        />
    </div>
    <div class="Notification__Body">
        <div class="flex flex-col">
            <div class="flex flex-col items-start sm:flex-row sm:items-center">
                <div class="Notification__Author">
                    <template
                        v-if="notification.send_by.first_name && notification.send_by.last_name"
                    >
                        {{ notification.send_by.first_name }} {{ notification.send_by.last_name }}
                    </template>
                    <template v-else>{{ notification.send_by.username }}</template>
                </div>
                <span class="Notification__Type">
                    {{ $t(notification.type) }}
                </span>
            </div>

            <div
                class="flex leading-tight flex-wrap text-sm font-medium text-gray-600 items-center"
            >
                <div class="Notification__Date">
                    {{ notification.send_at | dateFormat("DD/MM/YY HH:mm") }}
                </div>
                <div class="mx-2">&bull;</div>
                <SmartLink
                    v-if="notification.url"
                    class="text-gray-600 hover:text-blue-700 underline flex items-center"
                    :to="notification.url"
                >
                    {{ linkedObjectRepr }}
                </SmartLink>
            </div>
        </div>

        <template v-if="hasSubstring(notification.type, 'mention_')">
            <div v-if="!notification.url">
                {{ $t("deleted") }}
            </div>
            <div
                v-if="commentHtml"
                v-html="commentHtml"
                class="Notification__Content RichTextStyling"
            />
        </template>
        <template v-else-if="hasSubstring(notification.type, 'task_')">
            <div v-if="!notification.url">
                {{ $t("deleted") }}
            </div>
            <SmartLink
                v-else
                class="Notification__Content"
                :to="notification.url"
            >
                <div class="font-semibold">
                    {{ notification.linked_object.name | defaultVal($t("seeTargetUrl")) }}
                </div>
                <div
                    v-for="diff in showDiff(notification)"
                    class="text-sm font-medium text-gray-600"
                >
                    <div v-if="diff.field_name === 'done' && diff.after === true">
                        {{ $t("taskMarkedAsDone") }}
                    </div>
                    <div v-else-if="diff.field_name === 'done' && diff.after === false">
                        {{ $t("taskUndone") }}
                    </div>
                    <div v-else-if="diff.field_name === 'deadline' && diff.after === null">
                        {{ $t("deadlineDeleted") }}
                        <del>{{ diff.before | dateFormat }}</del>
                    </div>
                    <div v-else-if="diff.field_name === 'deadline' && diff.before === null">
                        {{ $t("deadlineAdded") }}
                        <ins>{{ diff.after | dateFormat }}</ins>
                    </div>
                    <div v-else-if="diff.field_name === 'deadline'">
                        {{ $t("deadlineUpdated") }}
                        <del>{{ diff.before | dateFormat }}</del>
                        &rarr;
                        <ins>{{ diff.after | dateFormat }}</ins>
                    </div>
                    <div v-else-if="diff.field_name === 'assignees' && diff.after === []">
                        {{ $t("ownersDeleted") }}
                        <del v-for="assignee in diff.before">
                            {{ assignee.repr }}
                        </del>
                    </div>
                    <div v-else-if="diff.field_name === 'assignees' && diff.before === []">
                        {{ $t("ownersAdded") }}
                        <ins v-for="assignee in diff.before">
                            {{ assignee.repr }}
                        </ins>
                    </div>
                    <div v-else-if="diff.field_name === 'assignees'">
                        {{ $t("ownersUpdated") }}
                        <del v-for="assignee in diff.before">
                            {{ assignee.repr }}
                        </del>
                        &rarr;
                        <ins v-for="assignee in diff.after">
                            {{ assignee.repr }}
                        </ins>
                    </div>
                </div>
            </SmartLink>
        </template>
        <template v-else>
            <div
                v-html="notification.content"
                class="Notification__Content"
            ></div>
        </template>

        <div class="Notification__Actions">
            <button
                class="button is-small my-2 is-outlined text-gray-500 border-gray-300"
                @click.prevent="toggleIsRead(notification)"
            >
                <span v-if="notification.is_read">{{ $t("markAsUnread") }}</span>
                <span v-else>{{ $t("markAsRead") }}</span>
            </button>
        </div>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

import { commentSchema } from "@richText/schema"
import { GLOModels, getTaskRepr, getGLORepr } from "@js/generic"

const NotificationType = {
    COPY_PROJECT: "copy_project",
    EXPORT_DESK: "export_desk",
    EXPORT_XLS: "export_xls",
    FEED_SAVED_FILTER: "feed_saved_filter",
    FEED_ACTIVITY: "feed_activity",
    INTERNAL_SHARED_FILTER: "internal_shared_filter",
    MENTION_COMMENT: "mention_comment",
    MENTION_ANNOTATION: "mention_annotation",
    REMINDER: "reminder",
    TASK_ASSIGNED: "task_assigned",
    TASK_UPDATED: "task_updated",
    TASK_TODO: "task_todo",
    TASK_DELETED: "task_deleted",
    VALIDATION_SHARING: "validation_sharing",
    VALIDATION_IDEA: "validation_idea",
}

export default {
    name: "NotificationElement",
    mixins: [PilotMixin],
    props: {
        listName: String,
        notification: Object,
    },
    data: () => ({
        showActions: false,
    }),
    computed: {
        commentHtml() {
            let comment_content

            if (this.notification.type == NotificationType.MENTION_COMMENT) {
                comment_content = _.get(this.notification, "data.comment.comment_content")
            }
            if (this.notification.type == NotificationType.MENTION_ANNOTATION) {
                comment_content = _.get(this.notification, "data.comment.content")
            }

            if (!comment_content) {
                return ""
            }
            return commentSchema.HTMLFromJSON(comment_content)
        },
        linkedObjectRepr() {
            if (
                this.notification.type == NotificationType.EXPORT_DESK ||
                this.notification.type == NotificationType.EXPORT_XLS
            ) {
                return this.$t("seeExport")
            }

            let glo = this.notification.linked_object
            if (!glo) {
                return ""
            }
            if (glo.model_name == GLOModels.TASK) {
                return getTaskRepr(glo.details)
            }
            return getGLORepr(glo)
        },
    },
    methods: {
        ...mapActions("notifications", ["toggleIsRead"]),
        hasSubstring(string, substring) {
            return string.indexOf(substring) !== -1
        },
        showDiff(notification) {
            if (notification.data && notification.data.diff) {
                return notification.data.diff
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                copy_project: "a terminé votre commande",
                export_desk: "a terminé votre commande",
                export_xls: "a terminé votre commande",
                feed_activity: "Evènement sur un filtre",
                feed_saved_filter: "Evènement sur un filtre",
                internal_shared_filter: "a partagé un de ses filtres avec vous",
                mention_annotation: "vous a mentionné dans une annotation",
                mention_comment: "vous a mentionné dans un commentaire",
                reminder: "Rappel",
                task_assigned: "vous a assigné une tâche",
                task_deleted: "Tâche supprimée",
                task_todo: "Tâche objet",
                task_updated: "a mis à jour une de vos tâches",
                validation_idea: "Validation de proposition",
                validation_sharing: "Validation",
                assignees: "Responsables",
                deadline: "A faire pour le",
                deadlineAdded: "Ajout d'une date de rendu",
                deadlineDeleted: "Suppression de la date de rendu",
                deadlineUpdated: "La date de rendu a été mise à jour",
                deleted: "L'objet lié a été supprimé",
                markAsRead: "Marquer la notification comme lue",
                markAsUnread: "Marquer comme non lue",
                ownersAdded: "Ajout de responsables",
                ownersDeleted: "Suppression de responsables",
                ownersUpdated: "Modification de la liste des responsables",
                seeExport: "Voir l'export",
                seeTargetUrl: "Voir plus de détails",
                sharedItem: "Contenu partagé",
                taskMarkedAsDone: "La tâche a été marquée comme terminée",
                taskUndone: "La tâche était terminée mais a été ré-activée",
            },
            en: {
                copy_project: "has completed your request",
                export_desk: "has finished your request",
                export_xls: "has completed your request",
                feed_activity: "Event on a filter",
                feed_saved_filter: "Event on a filter",
                internal_shared_filter: "shared one of its filters with you.",
                mention_annotation: "mentioned you in an annotation",
                mention_comment: "mentioned you in a comment",
                reminder: "Reminder",
                task_assigned: "assigned you a task",
                task_deleted: "Task deleted",
                task_todo: "Task object",
                task_updated: "updated one of your tasks",
                validation_idea: "Proposal validation",
                validation_sharing: "Validation",
                assignees: "Persons in charge",
                deadline: "To be done by",
                deadlineAdded: "Adding a render date",
                deadlineDeleted: "Delete the rendering date",
                deadlineUpdated: "The rendering date has been updated",
                deleted: "The linked object has been deleted",
                markAsRead: "Mark the notification as read",
                markAsUnread: "Mark as unread",
                ownersAdded: "Addition of managers",
                ownersDeleted: "Removal of managers",
                ownersUpdated: "Modification of the list of persons in charge",
                seeExport: "See the export",
                seeTargetUrl: "See more details",
                sharedItem: "Shared item",
                taskMarkedAsDone: "The task has been marked as completed",
                taskUndone: "The task was completed but has been reactivated",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
@import "~@sass/include_media.scss";

.Notification {
    @apply flex border border-gray-200 rounded bg-white my-4 p-5;
}

.Notification:first-child {
    @apply mt-0;
}

.Notification__Icon {
    @apply flex items-start flex-shrink-0 mr-2;
    @include media("<=phone") {
        display: none;
    }
}

.Notification__Body {
    @apply flex flex-col w-full;
}

.Notification__Author {
    @apply font-medium mr-1;
}

.Notification__Title {
    @apply flex items-center;
}

.Notification__Date {
}

.Notification__Content {
    @apply bg-gray-100 my-4 p-4 text-gray-900  break-words rounded;
}

.Notification__Actions {
    @apply flex items-center;
}

.Notification.isRead {
}

.Notification__Type {
    @apply flex items-center;
    > * {
        @apply mr-2;
    }
}

.Notification__More {
    width: 700px;
    min-height: 30rem;
    font-family: "Lucida Console", Monaco, monospace;
    line-height: 1.2;

    textarea {
        width: 100%;

        font-family: "Lucida Console", Monaco, monospace;
        font-size: 0.8rem;
        line-height: 1.2;
    }
}

.Notification__Icon {
}

.Notification__Actions {
    @apply flex items-center;
    :first-child {
        @apply mr-3;
    }
}
</style>
