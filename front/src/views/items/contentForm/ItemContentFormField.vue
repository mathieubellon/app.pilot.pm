<template>
<div class="ItemContentFormField">
    <template v-if="fieldSchema.elastic">
        <div v-for="(elasticSchema, index) in elasticSchemas">
            <!--
                 We define a :key attribute on those ItemContentFormFieldElement,
                 that are an important part of the rendering for elastic fields.
                 We want to prevent automatic component reusing by Vue when adding/deleting elastic fields,
                 so we force a re-render with the :key attribute.
                 It's important that this :key attribute include elasticSize in addition to the schema.name,
                 for the deletion use-case.
            -->
            <ItemContentFormFieldElement
                :key="`${elasticSchema.name}-#${elasticSize}`"
                :schema="elasticSchema"
                :validation="validation.content[elasticSchema.name]"
                :value="item.content[elasticSchema.name]"
                :warnings="warnings.content[elasticSchema.name]"
                @annotations="$emit('annotations', $event)"
                @input="$emit('input', $event)"
            >
                <template slot="labelOptions">
                    <Deletarium
                        v-if="elasticSize > 1"
                        deleteButtonClass="ItemContentFormField__deleteElasticElement Red"
                        :loadingName="`delete-${fieldSchema.name}-${index}`"
                        @delete="deleteElasticElement(index)"
                    />
                </template>
            </ItemContentFormFieldElement>
        </div>

        <div class="ItemContentFormField__addElasticElement">
            <a
                class="button is-xsmall"
                @click="addElasticElement"
            >
                {{ $t("addElasticElement") }} : {{ fieldSchema.label }}
            </a>
        </div>
    </template>

    <template v-else>
        <ItemContentFormFieldElement
            :schema="fieldSchema"
            :validation="validation.content[fieldSchema.name]"
            :value="item.content[fieldSchema.name]"
            :warnings="warnings.content[fieldSchema.name]"
            @annotations="$emit('annotations', $event)"
            @input="$emit('input', $event)"
        />
    </template>
</div>
</template>

<script>
import { mapState, mapGetters, mapActions, mapMutations } from "vuex"
import {
    getElasticFieldName,
    getElasticFieldSize,
    getElasticFieldSchemas,
} from "@js/items/itemsUtils"
import { EMPTY_PROSEMIRROR_DOC } from "@richText/schema"
import PilotMixin from "@components/PilotMixin"

import ItemContentFormFieldElement from "./ItemContentFormFieldElement"

export default {
    name: "ItemContentFormField",
    mixins: [PilotMixin],
    components: {
        ItemContentFormFieldElement,
    },
    props: {
        fieldSchema: {
            type: Object,
            required: true,
        },
        item: {
            required: true,
        },
        validation: {
            type: Object,
            required: true,
        },
        warnings: {
            type: Object,
            required: true,
        },
    },
    computed: {
        elasticSize() {
            return getElasticFieldSize(this.fieldSchema, this.item.content)
        },
        elasticSchemas() {
            return getElasticFieldSchemas(this.fieldSchema, this.item.content)
        },
    },
    methods: {
        ...mapMutations("loading", ["startLoading"]),
        addElasticElement() {
            let fieldName = getElasticFieldName(this.fieldSchema, this.elasticSize)
            let value = this.fieldSchema.initial || null
            // Ensure there's at least a minimal prosemirror doc
            if (this.fieldSchema.is_prosemirror && !value) {
                value = EMPTY_PROSEMIRROR_DOC
            }
            this.$emit("addElasticElement", { fieldName, value })
        },
        deleteElasticElement(index) {
            this.$emit("deleteElasticElement", {
                fieldName: this.fieldSchema.name,
                index,
            })
            this.startLoading(`delete-${this.fieldSchema.name}-${index}`)
        },
    },
    i18n: {
        messages: {
            fr: {
                addElasticElement: "+ Ajouter",
            },
            en: {
                addElasticElement: "+ Add",
                areYouSureDeletion: "Confirm deletion :",
            },
        },
    },
}
</script>
