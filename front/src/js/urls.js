import UrlTemplate from "./UrlTemplate"
import _ from "lodash"

let urls = {
    /** Initial Data **/
    initialData: "/api/initial/",
    languagesChoices: "/api/languages/",
    contentFieldSpecs: "/api/contentFieldsSpecs/",

    /** Activity **/
    activity: "/api/activity/",

    /** Assets **/
    assetsApp: "/assets/",
    assets: "/api/assets/:id/",
    assetsGetS3Signature: "/api/assets/get_s3_signature/",
    assetsStartConversion: "/api/assets/:id/start_conversion/",
    assetsStartZip: "/api/assets/start_zip/",
    assetsLibrary: "/api/assets/library/",
    assetsLinked: "/api/assets/linked/:contentTypeId/:objectId/",

    assetsLink: "/api/assets/:id/link/",
    assetsUnlink: "/api/assets/:id/unlink/",
    assetsCreateUrlAsset: "/api/assets/create_url_asset/:contentTypeId/:objectId/",

    assetsPublicGetS3Signature: "/api/assets/public/:token/get_s3_signature/",

    /** Asset Rights **/
    assetRights: "/api/asset_rights/:id/",

    /** Auth **/
    authLogin: "/api/auth/login/",
    authRegistration: "/api/auth/registration/",
    authPasswordReset: "/api/auth/password/reset/",
    authPasswordSet: "/api/auth/password/set/",
    authInvitationConfirm: "/api/auth/invitation/confirm/",

    /** Calendar **/
    calendarApp: "/items/calendar/",

    /** Channels **/
    channelsApp: "/channels/",
    channels: "/api/channels/:id/",
    channelsActive: "/api/channels/active/",
    channelsClosed: "/api/channels/closed/",
    channelChoices: "/api/channels/choices/",

    // Detail
    channelsClose: "/api/channels/:id/close/",
    channelsReopen: "/api/channels/:id/reopen/",
    channelsSoftDelete: "/api/channels/:id/soft_delete/",
    channelsUpdateState: "/api/channels/:id/update_state/",
    channelsRemoveItems: "/api/channels/:id/remove_items/",

    /** Comments **/
    commentsCreate: "/api/activity/create_comment/",
    commentsEdit: "/api/activity/edit_comment/",
    commentsDelete: "/api/activity/delete_comment/",

    /** Desk **/
    desks: "/api/desks/",
    desksCurrent: "/api/desks/current/",
    desksS3SignatureForLogo: "/api/desks/get_s3_signature_for_logo/",
    deskApp: "/desk/",
    deskSwitch: "/desk/switch/",

    /** Exports **/
    exports: "/api/exports/",

    /** Favorites **/
    favorites: "/api/favorites/:id/",

    /** I18N **/
    i18nSetlang: "/i18n/setlang/",

    /** Item types **/
    itemTypesApp: "/items/types/",
    itemTypes: "/api/items/types/:id/",

    /** Items **/
    // Item lists
    itemsApp: "/items/",
    itemsAppTrash: "/items/trash/",
    items: "/api/items/:id/",
    itemsTrashList: "/api/items/trash_list/",
    itemsForCalendar: "/api/items/calendar/",
    itemsForProject: "/api/items/for_project/:projectId/",
    itemsForChannel: "/api/items/for_channel/:channelId/",
    itemsChoices: "/api/items/choices/",

    // List actions
    itemsBulkAction: "/api/items/bulk_action/",
    itemsExportAll: "/api/items/export/",

    // Item detail
    itemUpdateWorkflowState: "/api/items/:id/update_workflow_state/",
    itemsSession: "/api/items/:itemId/sessions/:id/",
    itemDiff: "/api/items/:id/diff/:leftSessionId/:rightSessionId/",
    itemExport: "/items/:id/export/",

    itemUpdateContent: "/api/items/:id/update_content/",
    itemPutInTrash: "/api/items/:id/put_in_trash/",
    itemRestoreFromTrash: "/api/items/:id/restore_from_trash/",
    itemSoftDelete: "/api/items/:id/soft_delete/",
    itemCreateMajorVersion: "/api/items/:id/create_major_version/",
    itemRestoreSession: "/api/items/:id/restore_session/",

    // Public API ( for SharingApp )
    itemsShared: "/api/shared/:token/items/list/",
    itemsSharedForCalendar: "/api/shared/:token/items/calendar/",

    /** Item Filters **/
    savedFilters: "/api/saved_filters/:id/",
    savedFiltersExport: "/api/saved_filters/:id/export/",
    internalSharedFilters: "/api/internal_shared_filters/:id/",

    /** Labels **/
    labelsApp: "/labels/",
    labels: "/api/labels/:id/",
    labelsSetOrder: "/api/labels/set_order/",
    labelsBulkAction: "/api/labels/bulk_action/",
    labelsMerge: "/api/labels/merge/",

    /** List Config **/
    listConfig: "/api/list_config/:name/",
    // Public API ( for SharingApp )
    listConfigShared: "/api/shared/:token/list_config/:name/",

    /** Notifications **/
    notifications: "/api/notifications/:id/",
    notificationsSubset: "/api/notifications/:listName/",
    notificationsSetAllRead: "/api/notifications/set_all_read/",

    // Notification feed
    notificationFeeds: "/api/notification_feeds/:id/",

    /** Reminders **/
    reminders: "/api/reminders/:id/",

    /** Projects **/
    projectsApp: "/projects/",

    // Lists
    projects: "/api/projects/:id/",
    projectsIdea: "/api/projects/idea/",
    projectsActive: "/api/projects/active/",
    projectsClosed: "/api/projects/closed/",
    projectsForCalendar: "/api/projects/calendar/",
    projectsChoices: "/api/projects/choices/",
    projectsExportAll: "/api/projects/export/",

    // Detail
    projectsCopy: "/api/projects/:id/copy/",
    projectsClose: "/api/projects/:id/close/",
    projectsSoftDelete: "/api/projects/:id/soft_delete/",
    projectsUpdateState: "/api/projects/:id/update_state/",
    projectsRemoveItems: "/api/projects/:id/remove_items/",

    // Public API ( for SharingApp )
    projectsSharedForCalendar: "/api/shared/:token/projects/calendar/",

    /** Search **/
    search: "/api/search/:docType/",

    /** Sharings **/
    sharingsApp: "/sharings/",
    sharings: "/api/sharings/:token/",
    sharingsPaginated: "/api/sharings/paginated/",
    sharingsDeactivate: "/api/sharings/:token/deactivate/",
    sharingsBulkAction: "/api/sharings/bulk_action/",

    // Public API ( for SharingApp )
    sharedItem: "/api/shared/:token/items/:itemId/",
    sharedItemFeedback: "/api/shared/:token/feedbacks/",

    /** Subscription **/
    subscriptionApp: "/subscription/",
    subscription: "/api/subscription/",
    subscriptionChange: "/api/subscription/change/",
    subscriptionChangeCard: "/api/subscription/change_card/",
    subscriptionDeactivateDesk: "/api/subscription/deactivate_desk/",
    subscriptionTerminate: "/api/subscription/terminate/",
    subscriptionUpdateBillingAddress: "/api/subscription/update_billing_address/",

    /** Subscription Plans **/
    subscriptionPlans: "/api/plans/",

    /** Targets **/
    targetsApp: "/targets/",
    targets: "/api/targets/:id/",
    targetsChoices: "/api/targets/choices/",

    /** Tasks **/
    tasks: "/api/tasks/:id/",
    tasksLinked: "/api/tasks/linked/:contentTypeId/:objectId/",
    tasksSetOrder: "/api/tasks/set_order/",
    tasksSendNotifications: "/api/tasks/:id/send_notifications/",
    tasksImportTaskGroup: "/api/tasks/import_task_group/",
    tasksOfCurrentUser: "/api/tasks/:listName/",

    // Default Task Group admin
    taskGroupApp: "/tasks/groups/",
    tasksGroups: "/api/tasks_groups/:id/",
    tasksTemplates: "/api/tasks_templates/:id/",
    tasksTemplatesSetOrder: "/api/tasks_templates/set_order/",

    /** Teams **/
    teamsApp: "/users/teams/:id/",
    teams: "/api/teams/:id/",

    /** Users **/
    usersApp: "/users/",
    users: "/api/users/:id/",
    usersInactives: "/api/users/deactivated/",
    usersInvitation: "/api/users_invitations/:id/",
    usersInvitationSendAgain: "/api/users_invitations/:id/send_again/",
    usersChoices: "/api/users/choices/",
    usersDeactivate: "/api/users/:id/deactivate/",
    usersReactivate: "/api/users/:id/reactivate/",
    usersWipeout: "/api/users/:id/wipeout/",
    usersUpdatePermission: "/api/users/:id/update_permission/",
    usersUpdateTeams: "/api/users/:id/update_teams/",
    usersS3SignatureForAvatar: "/api/users/me/get_s3_signature_for_avatar/",
    usersExportAll: "/api/users/export/",

    // Users me
    usersMe: "/api/users/me/",
    usersMeChangePassword: "/api/users/me/change_password/",
    usersMeSetMessageAsRead: "/api/users/me/set_message_as_read/",

    // Change notification
    usersChangeNotificationPreferences: "/api/notification_preferences/:token/",

    /** Wiki **/
    wikiApp: "/wiki/",
    wikiHomePage: "/api/wiki_pages/home/",
    wikiPages: "/api/wiki_pages/:id/",

    /** Workflow **/
    workflowStatesApp: "/workflow/states/",
    workflowStates: "/api/workflow/states/:id/",
    workflowStatesSetOrder: "/api/workflow/states/set_order/",

    /** Integrations **/
    integrationsApp: "/integrations/tokens/",
    integrationsApiTokens: "/api/api_tokens/:id/",
}

urls = _.mapValues(urls, (url) => new UrlTemplate(url))

export default urls
