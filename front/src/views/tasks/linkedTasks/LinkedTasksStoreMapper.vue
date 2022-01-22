<script>
import {
    mapInstanceState,
    mapInstanceGetters,
    mapInstanceMutations,
    mapInstanceActions,
} from "@js/lib/vuex-helpers"

const getNamespace = (vm) => `${vm.namespace}/linkedTasks`

export default {
    name: "LinkedTasksStoreMapper",
    props: {
        namespace: String,
    },
    computed: {
        ...mapInstanceState(getNamespace, [
            "linkedTasks",
            "contentType",
            "objectId",
            "taskToEdit",
            "fieldsCurrentlyUpdating",
        ]),
        ...mapInstanceGetters(getNamespace, [
            "publicationTask",
            "linkedTasksTodo",
            "currentTaskTodo",
            "getNextTaskToDo",
        ]),
    },
    methods: {
        ...mapInstanceMutations(getNamespace, [
            "initLinkedTasksStore",
            "setLinkedTasks",
            "updateLinkedTask",
            "removeLinkedTask",
            "setTaskToEdit",
            "startFieldsCurrentlyUpdating",
            "stopFieldsCurrentlyUpdating",
        ]),
        ...mapInstanceActions(getNamespace, [
            "fetchLinkedTasks",
            "createTask",
            "partialUpdateTask",
            "saveCurrentTaskOrder",
            "deleteTask",
            "sendNotification",
            "importTaskGroup",
        ]),
    },
}
</script>
