<template>
<div class="ProjelDetailTopbar flex items-end w-full">
    <div class="bg-white mr-2 py-0">
        <Icon
            class="text-gray-400 w-5"
            :name="iconName"
        />
    </div>
    <Spinner v-if="fieldsCurrentlyUpdating.title" />
    <template v-else>
        <span
            v-if="isProjectRoute"
            class="text-gray-500 mx-1 text-center"
        >
            #{{ projel.id }}
        </span>
        <input
            v-if="isNameInEdition"
            v-model="nameEdited"
            class="nameEditionInput font-bold"
            ref="nameEditionInput"
            @blur="endNameEdition"
            @keyup.enter="endNameEdition"
        />
        <div
            v-else
            class="cursor-pointer"
            @click="setIsNameInEdition(true)"
        >
            {{ projel.name }}
        </div>
    </template>
</div>
</template>

<script>
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ProjelDetailTopbar",
    mixins: [PilotMixin],
    data: () => ({
        nameEdited: "",
    }),
    computed: {
        ...mapState("projelDetail", ["projel", "fieldsCurrentlyUpdating", "isNameInEdition"]),
        ...mapGetters("projelDetail", ["isChannelRoute", "isProjectRoute"]),
        iconName() {
            return this.isChannelRoute ? "Channel" : "Project"
        },
    },
    watch: {
        isNameInEdition() {
            if (this.isNameInEdition) {
                this.startNameEdition()
            }
        },
    },
    methods: {
        ...mapMutations("projelDetail", ["setIsNameInEdition"]),
        ...mapActions("projelDetail", ["partialUpdateProjel"]),
        startNameEdition() {
            this.nameEdited = this.projel.name
            this.$nextTick(() => {
                $(this.$refs.nameEditionInput).focus()
            })
        },
        endNameEdition() {
            this.partialUpdateProjel({
                name: this.nameEdited,
            }).then(() => this.setIsNameInEdition(false))
        },
    },
}
</script>
