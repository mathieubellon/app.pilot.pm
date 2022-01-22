<template>
<OffPanel :name="name">
    <div slot="offPanelTitle">{{ title }}</div>
    <div slot="offPanelBody">
        <AutoForm
            :initialData="initialData"
            :saveUrl="saveUrl"
            :schema="schema"
            @cancel="closeOffPanel(name)"
            @saved="onSaved"
        />
    </div>
</OffPanel>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

import OffPanel from "@components/OffPanel.vue"
import AutoForm from "@components/forms/AutoForm"

export default {
    name: "AutoFormInPanel",
    components: {
        OffPanel,
        AutoForm,
    },
    data: () => ({
        initialData: {},
    }),
    props: {
        name: String,
        title: String,
        schema: Array,
        saveUrl: { required: true },
    },
    methods: {
        ...mapMutations("offPanel", ["openOffPanel", "closeOffPanel"]),
        onSaved(instance) {
            this.$emit(this.initialData.id ? "updated" : "created", instance)
            this.closeOffPanel(this.name)
        },
        openFormPanel(initialData = {}) {
            this.initialData = initialData
            this.openOffPanel(this.name)
        },
    },
}
</script>
