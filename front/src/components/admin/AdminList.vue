<template>
<div>
    <SlickList
        v-if="sortable && (!checkPerm || myPermissions.is_admin)"
        axis="y"
        :distance="5"
        helperClass="AdminList__SortableHelper"
        lockAxis="y"
        :lockToContainerEdges="true"
        :value="instancesList"
        @input="$emit('sorted', $event)"
    >
        <transition-group
            enter-active-class="animated fadeInDown"
            leave-active-class="animated fadeOut"
            tag="div"
        >
            <SlickItem
                v-for="(instance, instanceIndex) in instancesList"
                class="AdminList__listElement sortable"
                :index="instanceIndex"
                :key="instance.id"
            >
                <span class="AdminList__reorderHandle">
                    <Icon name="MoveHandle" />
                </span>

                <div class="AdminList__listElement__content">
                    <slot :instance="instance" />
                </div>

                <AdminListActions
                    v-if="showActions"
                    :checkPerm="checkPerm"
                    @delete="$emit('delete', instance)"
                    @deletionCancelled="$emit('deletionCancelled', instance)"
                    @deletionRequested="$emit('deletionRequested', instance)"
                    @edit="$emit('edit', instance)"
                />
            </SlickItem>
        </transition-group>
    </SlickList>

    <div v-else>
        <transition-group
            enter-active-class="animated fadeInDown"
            leave-active-class="animated fadeOut"
            tag="div"
        >
            <div
                v-for="instance in instancesList"
                class="AdminList__listElement"
                :key="instance.id"
            >
                <div class="AdminList__listElement__content">
                    <slot :instance="instance" />
                </div>

                <AdminListActions
                    v-if="showActions"
                    :checkPerm="checkPerm"
                    @delete="$emit('delete', instance)"
                    @deletionCancelled="$emit('deletionCancelled', instance)"
                    @deletionRequested="$emit('deletionRequested', instance)"
                    @edit="$emit('edit', instance)"
                />
            </div>
        </transition-group>
    </div>
</div>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import Icon from "@components/Icon.vue"
import { SlickList, SlickItem } from "vue-slicksort"
import AdminListActions from "@components/admin/AdminListActions.vue"

export default {
    name: "AdminList",
    components: {
        SlickList,
        SlickItem,
        AdminListActions,
        Icon,
    },
    props: {
        instancesList: Array,
        sortable: Boolean,
        showActions: {
            type: Boolean,
            default: true,
        },
        checkPerm: {
            type: Boolean,
            default: true,
        },
    },
    computed: {
        ...mapGetters("users", ["myPermissions"]),
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
@import "~@sass/include_media.scss";

.AdminList__listElement {
    @apply flex flex-grow items-center bg-white rounded mb-1 border border-gray-200 p-3;

    &:hover {
        @apply rounded bg-gray-100 border-gray-200;
    }

    &.sortable {
        cursor: grab;
    }

    @include media("<=tablet") {
        @apply flex-col items-start p-4;
    }
}

.AdminList__listElement__content {
    @apply flex flex-grow items-center p-3;
}

.AdminList__listElement__order {
    margin-right: 10px;
}

.AdminList__reorderHandle {
    font-size: 1.3em;
    color: $gray-dark;
}

.AdminList__SortableHelper {
    z-index: 20;
}
</style>
