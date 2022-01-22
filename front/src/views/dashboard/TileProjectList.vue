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
                            @click.prevent="setOrdering('-start')"
                        >
                            {{ $t("startDateFirst") }}
                        </button>
                        <button
                            class="menu-item"
                            @click.prevent="setOrdering('priority')"
                        >
                            {{ $t("priorityHighestFirst") }}
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
            class="DashboardTile__body__empty"
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
                class="dashboardProjectList"
                :key="currentPage"
            >
                <ProjectListElement
                    v-for="project in tileList"
                    :key="project.id"
                    :project="project"
                ></ProjectListElement>
            </div>
        </transition>
    </div>

    <div class="DashboardTile__pagination">
        <div>
            <a
                class="button mr-1"
                :class="{ disabled: previous_page === null }"
                @click.prevent="fetchProjects(1)"
            >
                {{ $t("start") }}
            </a>
            <a
                class="button"
                :class="{ disabled: previous_page === null }"
                @click.prevent="fetchProjects(previous_page)"
            >
                {{ $t("previous") }}
            </a>
        </div>
        <div>{{ currentPage }}/{{ num_pages }}</div>
        <a
            class="button"
            :class="{ disabled: next_page === null }"
            @click.prevent="fetchProjects(next_page, 'fadeInRight')"
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
import ProjectListElement from "@views/projects/list/ProjectListElement.vue"
import MenuItemWithConfirm from "@components/MenuItemWithConfirm"

export default {
    name: "TileProjectList",
    mixins: [TileMixin, PilotMixin],
    components: {
        ProjectListElement,
        MenuItemWithConfirm,
    },
    data: () => ({
        ordering: null,
        transition: "fadeInLeft",
        tileList: [],
    }),
    watch: {
        ordering() {
            this.fetchProjects()
        },
    },
    methods: {
        setOrdering(ordering) {
            this.ordering = ordering
        },
        fetchProjects(page = 1, transition = "fadeInLeft") {
            this.transition = transition

            let queryParamSerializer = new QueryParamSerializer(this.tile.queryParams)
            queryParamSerializer.setParam("page", page)
            if (this.ordering) {
                queryParamSerializer.setParam("order_by", this.ordering)
            }
            if (this.tile.filterOwnersOnUserMe) {
                queryParamSerializer.setParam("owners", this.$store.state.users.me.id)
            }
            if (this.tile.filterMembersOnUserMe) {
                queryParamSerializer.setParam("members", this.$store.state.users.me.id)
            }

            $httpX({
                name: "fetchProjects",
                method: "GET",
                commit: this.$store.commit,
                url: urls.projectsActive,
                params: queryParamSerializer.params,
            }).then((response) => {
                this.num_pages = response.data.num_pages
                this.next_page = response.data.next
                this.previous_page = response.data.previous
                this.tileList = response.data.objects
            })
        },
    },
    mounted() {
        this.fetchProjects()
    },
    i18n: {
        messages: {
            fr: {
                updatedAtFirst: "date de mise à jour",
                startDateFirst: "date de début",
                priorityHighestFirst: "priorité",
            },
            en: {
                updatedAtFirst: "updated date",
                startDateFirst: "start date",
                priorityHighestFirst: "priority",
            },
        },
    },
}
</script>

<style lang="scss">
.dashboardProjectList {
    .Project__title {
        @apply text-sm;
    }
    .ProjectListElement {
        @apply p-2;
        box-shadow: 1px 2px 4px rgba(0, 0, 0, 0.03);
    }

    .ProjectListElement__Icon {
        display: none;
    }
}
</style>
