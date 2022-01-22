<template>
<div class="ItemPicker">
    <div class="ItemPicker__Toolbar">
        <BigFilter
            class="ItemPicker__BigFilter"
            :apiSource="apiSource"
            filterSchemaUrl="/api/big_filter/schema/items/list/"
        />
        <ItemOrdering
            class="ItemPicker__Ordering"
            :value="apiSource.ordering"
            @orderingChange="apiSource.setOrdering"
        />
    </div>
    <ItemList context="picker" />
</div>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import urls from "@js/urls"
import { getInMemoryApiSource } from "@js/apiSource"

import BigFilter from "@views/bigFilter/BigFilter"
import ItemList from "@views/items/list/ItemList"
import ItemOrdering from "@views/items/list/ItemOrdering"

export default {
    name: "ItemPicker",
    components: {
        BigFilter,
        ItemOrdering,
        ItemList,
    },
    computed: {
        ...mapState("itemList", ["items", "apiSource"]),
    },
    methods: {
        ...mapMutations("itemList", ["setApiSource"]),
        ...mapActions("itemList", ["fetchItemList"]),
    },
    created() {
        this.setApiSource(getInMemoryApiSource(urls.items))
        this.fetchItemList()
    },
}
</script>

<style lang="scss">
.ItemPicker__Toolbar {
    margin: 1em 0;
    padding: 0.5em 0 0 0;
    display: flex;
    align-items: center;
    width: 100%;
    flex-flow: row;
    flex-shrink: 0;
}
.ItemPicker__BigFilter {
    min-width: 300px;
    flex-grow: 1;
}
.ItemPicker__Ordering {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-shrink: 0;
    margin-left: 1em;
}
</style>
