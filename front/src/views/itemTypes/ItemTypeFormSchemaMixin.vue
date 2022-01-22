<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import ItemTypeIconSelect from "./ItemTypeIconSelect"

export default {
    name: "ItemTypeFormSchemaMixin",
    computed: {
        ...mapGetters("choices", ["taskGroupChoices"]),
        itemTypeFormSchema() {
            return [
                {
                    name: "name",
                    type: "char",
                    label: this.$t("name"),
                    placeholder: this.$t("name"),
                    required: true,
                },
                {
                    name: "description",
                    type: "text",
                    label: this.$t("description"),
                    placeholder: this.$t("description"),
                },
                {
                    name: "task_group_id",
                    type: "choice",
                    choices: this.taskGroupChoices,
                    label: this.$t("defaultTasksGroup"),
                },
                {
                    name: "icon_name",
                    component: ItemTypeIconSelect,
                    label: this.$t("icon"),
                    required: true,
                },
            ]
        },
    },
    i18n: {
        messages: {
            fr: {
                defaultTasksGroup: "Groupe de tâches par défaut",
                icon: "Icone",
            },
            en: {
                defaultTasksGroup: "Default tasks group",
                icon: "Icon",
            },
        },
    },
}
</script>
