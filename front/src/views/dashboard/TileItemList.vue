<template>
<div class="DashboardTile">
    <div class="DashboardTile__header">
        <span>{{ tile.title }}</span>

        <Popper triggerElementName="PopperRef">
            <template #triggerElement>
                <button ref="PopperRef">
                    <Icon name="MenuDotsHorizontal" />
                </button>
            </template>

            <template #content>
                <div class="w-40">
                    <template v-if="tileList.length > 0">
                        <div class="text-sm font-semibold">{{ $t("sortBy") }}</div>
                        <button
                            class="menu-item"
                            @click.prevent="setOrdering('-updated_at')"
                        >
                            {{ $t("updatedAtFirst") }}
                        </button>
                        <button
                            class="menu-item"
                            @click.prevent="setOrdering('-publication_dt')"
                        >
                            {{ $t("publicationDateFirst") }}
                        </button>
                    </template>
                    <div class="text-sm font-semibold">{{ $t("actions") }}</div>
                    <MenuItemWithConfirm
                        iconName="Trash"
                        :isRed="true"
                        :label="$t('remove')"
                        @confirmed="removeTileFromUserTiles(tileIndex)"
                    />
                </div>
            </template>
        </Popper>
    </div>
    <div class="DashboardTile__body">
        <div
            v-if="tileList.length == 0"
            class=""
        >
            {{ $t("emptyTile") }}&nbsp;
            <a @click.prevent="removeTileFromUserTiles(tileIndex)">({{ $t("remove") }}?)</a>
        </div>
        <transition
            :duration="{ leave: 300, enter: 500 }"
            :enter-active-class="`animated ${transition}`"
            mode="out-in"
        >
            <div
                v-if="tileList.length > 0"
                class="itemsList"
                :key="currentPage"
            >
                <ItemListElement
                    v-for="item in tileList"
                    context="dashboard"
                    :item="item"
                    :key="item.id"
                    @itemStateChanged="onItemStateChanged"
                />
            </div>
        </transition>
    </div>
    <div class="DashboardTile__pagination">
        <div>
            <a
                class="button mr-1"
                :class="{ disabled: previous_page === null }"
                @click.prevent="fetchItems(1)"
            >
                {{ $t("start") }}
            </a>
            <a
                class="button"
                :class="{ disabled: previous_page === null }"
                @click.prevent="fetchItems(previous_page)"
            >
                {{ $t("previous") }}
            </a>
        </div>
        <div>{{ currentPage }}/{{ num_pages }}</div>
        <a
            class="button"
            :class="{ disabled: next_page === null }"
            @click.prevent="fetchItems(next_page, 'fadeInRight')"
        >
            {{ $t("next") }}
        </a>
    </div>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { QueryParamSerializer } from "@js/queryString"

import TileMixin from "./TileMixin.vue"
import ItemListElement from "@views/items/list/ItemListElement.vue"
import MenuItemWithConfirm from "@components/MenuItemWithConfirm"

export default {
    name: "TileItemList",
    mixins: [TileMixin, PilotMixin],
    components: {
        ItemListElement,
        MenuItemWithConfirm,
    },
    data: () => ({
        ordering: null,
        transition: "fadeInLeft",
        tileList: [],
    }),
    watch: {
        ordering() {
            this.fetchItems()
        },
    },
    methods: {
        setOrdering(ordering) {
            this.ordering = ordering
        },
        fetchItems(page = 1, transition = "fadeInLeft") {
            this.transition = transition

            let queryParamSerializer = new QueryParamSerializer(this.tile.queryParams)
            queryParamSerializer.setParam("page", page)
            if (this.ordering) {
                queryParamSerializer.setParam("order_by", this.ordering)
            }
            if (this.tile.filterOwnersOnUserMe) {
                queryParamSerializer.setParam("owners", this.$store.state.users.me.id)
            }

            $httpX({
                name: "fetchItems",
                method: "GET",
                commit: this.$store.commit,
                url: urls.items,
                params: queryParamSerializer.params,
            }).then((response) => {
                this.num_pages = response.data.num_pages
                this.next_page = response.data.next
                this.previous_page = response.data.previous
                this.tileList = response.data.objects
            })
        },
        onItemStateChanged(item) {
            this.tileList = this.tileList.map((oldItem) => (oldItem.id == item.id ? item : oldItem))
        },
    },
    mounted() {
        this.fetchItems()
    },
    i18n: {
        messages: {
            fr: {
                updatedAtFirst: "date de mise à jour",
                publicationDateFirst: "date de publication",
            },
            en: {
                updatedAtFirst: "updated date",
                publicationDateFirst: "start date",
            },
        },
    },
}
</script>
