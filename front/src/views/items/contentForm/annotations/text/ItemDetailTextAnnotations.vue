<template>
<Fragment>
    <div
        v-for="(annotationManager, fieldName) in annotationManagers"
        class="ItemDetailTextAnnotations"
        :key="fieldName"
    >
        <template v-if="annotationManager.type == 'text'">
            <AnnotationElement
                v-if="!annotation.resolved"
                v-for="annotation in annotationManager.selectedAnnotations"
                :annotation="annotation"
                :annotationManager="annotationManager"
                :key="annotation.id"
                :readOnly="readOnly"
            />
        </template>
    </div>
</Fragment>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { Fragment } from "vue-fragment"
import AnnotationElement from "../AnnotationElement.vue"
import BoxEscapingWatcher from "@js/BoxEscapingWatcher"

export default {
    name: "ItemDetailTextAnnotations",
    components: {
        Fragment,
        AnnotationElement,
    },
    props: {
        annotationManagers: Object,
        readOnly: Boolean,
    },
    computed: {
        allSelectedTextAnnotations() {
            return _.flatten(
                _.map(this.annotationManagers, (am) =>
                    am.type == "text" ? am.selectedAnnotations : [],
                ),
            )
        },
    },
    methods: {
        ...mapActions("itemContentForm", ["deselectAllAnnotations"]),
    },
    watch: {
        allSelectedTextAnnotations() {
            if (this.annotationEscapingWatcher && this.allSelectedTextAnnotations.length) {
                this.annotationEscapingWatcher.startWatching()
            }
        },
    },
    mounted() {
        if (!this.readOnly) {
            this.annotationEscapingWatcher = new BoxEscapingWatcher(
                () => [
                    ...document.querySelectorAll(".ItemDetailTextAnnotations"),
                    ...document.querySelectorAll(".CommentBox__mentionsDropdown"),
                ],
                () => {
                    this.deselectAllAnnotations()
                    this.annotationEscapingWatcher.stopWatching()
                },
            )
        }
    },
    beforeDestroy() {
        if (this.annotationEscapingWatcher) {
            this.annotationEscapingWatcher.stopWatching()
        }
    },
}
</script>

<style lang="scss">
@import "~@sass/business/items_vars.scss";

.ItemDetailTextAnnotations {
    @include itemDecorationBoxes();
}
</style>
