<template>
<div class="form__field">
    <div class="form__field__label">
        {{ label }}
    </div>
    <div class="mb-4">
        {{ content }}
        <!--
        <a :href="url" v-if="me.is_admin || me.is_editor">
            {{ $t('create') }}
        </a>
        --></div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

const TYPES = ["channel", "project", "target"]

export default {
    name: "EmptyRelations",
    props: {
        type: {
            type: String,
            validator: (value) => {
                return TYPES.indexOf(value) !== -1
            },
        },
    },
    computed: {
        ...mapState("users", ["me"]),
        label() {
            return {
                channel: this.$t("channel"),
                project: this.$t("project"),
                target: this.$t("target"),
            }[this.type]
        },
        content() {
            return {
                channel: this.$t("noChannel"),
                project: this.$t("noProject"),
                target: this.$t("noTarget"),
            }[this.type]
        },
        url() {
            return {
                channel: "/channels/add/",
                project: "/projects/add/",
                target: "/targets/add/",
            }[this.type]
        },
    },
}
</script>
