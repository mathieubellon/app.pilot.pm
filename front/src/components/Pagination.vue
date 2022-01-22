<template>
<span
    v-if="pagination"
    class="relative z-0 inline-flex shadow-sm rounded-md"
>
    <button
        class="list-action-button rounded-l-sm rounded-r-none"
        :disabled="pagination.previous === null"
        type="button"
        @click="$emit('pageChange', pagination.previous)"
    >
        {{ $t("previous") }}
    </button>
    <Popper
        closeOnClickSelector=".willClose"
        triggerElementName="paginationPopper"
        triggerType="click"
    >
        <template #triggerElement>
            <button
                class="-ml-px list-action-button rounded-none"
                ref="paginationPopper"
                :disabled="pagination.num_pages == 1"
                type="button"
            >
                {{ $t("page") }} {{ currentPage | defaultVal(1) }} / {{ pagination.num_pages }}
                <!-- The empty span is required to correctly align with flex display -->
                <span>
                    <Icon
                        class="caret"
                        :class="{ 'text-gray-300': pagination.num_pages == 1 }"
                        name="ChevronDown"
                    />
                </span>
            </button>
        </template>

        <template #content>
            <div
                class="w-32 overflow-y-auto"
                style="max-height: 24rem"
            >
                <button
                    v-for="pageNum of pagination.num_pages"
                    class="menu-item"
                    :class="{ disabled: pageNum == currentPage }"
                    @click="$emit('pageChange', pageNum)"
                >
                    {{ $t("page") }} {{ pageNum }}
                </button>
            </div>
        </template>
    </Popper>
    <button
        class="-ml-px list-action-button rounded-l-none rounded-r-sm"
        :disabled="pagination.next === null"
        type="button"
        @click="$emit('pageChange', pagination.next)"
    >
        {{ $t("next") }}
    </button>
</span>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "Pagination",
    mixins: [PilotMixin],
    props: {
        pagination: Object,
    },
    computed: {
        currentPage() {
            if (!this.pagination) {
                return null
            }
            return this.pagination.previous ? this.pagination.previous + 1 : 1
        },
    },
    i18n: {
        messages: {
            fr: {
                page: "Page",
            },
            en: {
                page: "Page",
            },
        },
    },
}
</script>
