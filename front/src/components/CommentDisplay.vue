<template>
<div class="CommentDisplay">
    <div
        v-html="newCommentDisplay"
        class="RichTextStyling"
        @click="onClick"
    />
</div>
</template>

<script>
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import urls from "@js/urls"
import { commentSchema } from "@richText/schema"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "CommentDisplay",
    mixins: [PilotMixin],
    props: {
        comment: Object,
    },
    computed: {
        newCommentDisplay() {
            return commentSchema.HTMLFromJSON(this.comment)
        },
    },
    methods: {
        ...mapMutations("offPanel", ["openOffPanel"]),
        ...mapActions("users", ["fetchUserExamined"]),
        onClick(event) {
            let $target = $(event.target)
            if (!$target.hasClass("mention")) {
                return
            }

            let entity = $target.attr("entity"),
                id = $target.attr("id")

            if (entity == "team") {
                this.$router.push(urls.teamsApp.format({ id }))
            } else if (entity == "user") {
                this.fetchUserExamined(id)
                this.openOffPanel("UserExaminationPanel")
            }
        },
    },
}
</script>

<style lang="scss">
.CommentDisplay {
    word-wrap: break-word;
    overflow-wrap: break-word;
    overflow-y: hidden;
}
.CommentDisplay .RichTextStyling {
    & > p:first-child {
        margin-top: 0;
    }
    & > p:last-child {
        margin-bottom: 0;
    }
}

.CommentDisplay .mention {
    &.team,
    &.user {
        cursor: pointer;
    }
}
</style>
