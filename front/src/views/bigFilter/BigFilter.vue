<template>
<div class="BigFilter flex items-center mb-4">
    <button
        class="button rounded-sm is-light flex py-2 rounded-r-none"
        type="button"
        @click="openFilteringDropdown($event)"
    >
        {{ $t("addFilter") }}
        <!-- The empty span is required to correctly align with flex display -->
        <span>
            <Icon
                class="text-gray-400 caret"
                name="ChevronDown"
            />
        </span>
    </button>
    <!-- Free search input-->
    <!-- /!\ BIG FAT WARNING : DO NOT REMOVE the relative class,
    it is required for the correct positioning of BigFilter__searchHintDropdown /!\-->
    <div
        class="relative flex-1"
        @keydown.enter="selectFreeSearch()"
    >
        <input
            class="BigFilter__searchInput"
            ref="filterInput"
            :placeholder="placeholder"
            v-model.trim="filterInputValue"
            @blur="searchInputFocused = false"
            @focus="searchInputFocused = true"
        />

        <transition
            enter-active-class="animated fadeIn"
            leave-active-class="animated fadeOut"
        >
            <div
                v-if="searchInputFocused"
                class="BigFilter__searchHintDropdown"
                :class="{ 'cursor-pointer': filterInputValue }"
                @click.prevent="selectFreeSearch()"
            >
                <template v-if="filterInputValue">
                    {{ $t("hitEnterToSearchFor") }}
                    <span class="bg-yellow-300 text-black rounded-sm py-0.5 px-1">
                        "{{ filterInputValue }}"
                    </span>
                    {{ $t("inTitleOrContent") }}
                </template>
                <template v-else>
                    {{ $t("typeTextToSearch") }}
                </template>
            </div>
        </transition>
    </div>
    <!-- Current filter items list -->
    <div class="w-full flex flex-wrap items-center">
        <div
            v-for="(filterItem, index) in filterItems"
            class="BigFilter__filterItem"
            :class="{ 'mr-2': index == filterItems.length - 1 }"
            @click.stop="openFilteringDropdown($event, filterItem, index)"
        >
            <span
                class="BigFilter__filterItemDescription"
                :class="{
                    'cursor-default hover:bg-blue-50': filterItem.category.type == 'search',
                }"
            >
                <span class="truncate flex-grow">
                    <span class="text-blue-900">{{ filterItem.category.label }}</span>
                    <span class="">{{ filterItem.label }}</span>
                </span>
                <Icon
                    v-if="filterItem.category.type != 'search'"
                    class="text-blue-900 caret"
                    name="ChevronDown"
                />
            </span>
            <a
                class="flex items-center justify-center"
                @click.stop="removeFilterItem(index)"
            >
                <Icon
                    class="text-blue-900 hover:text-red-700"
                    name="Close"
                    size="14px"
                />
            </a>
        </div>

        <SavedFilterBigFilterSaveButton
            v-if="canSave"
            :apiSource="apiSource"
        />
    </div>

    <!-- Dropdowns -->
    <div
        v-show="isFilteringDropdownVisible"
        class="popper"
        ref="filteringDropdown"
    >
        <!-- Categories dropdowns -->
        <div
            v-if="isCategoryDropdownVisible()"
            class="BigFilter__filteringDropdown"
        >
            <div
                v-for="category in filterSchema"
                class="menu-item py-1"
                :class="{
                    disabled: isCategoryDisabled(category),
                }"
                :key="category.name"
                @click.prevent="selectCategory(category)"
            >
                <Icon
                    v-if="category.icon"
                    :name="category.icon"
                />
                <div
                    v-else
                    class="mr-3"
                    style="width: 20px"
                />

                <div class="flex flex-col items-start">
                    <span>
                        {{ category.label }}
                        <template v-if="isCategoryDisabled(category)">
                            ( {{ $t("alreadyUsed") }} )
                        </template>
                    </span>
                    <span class="menu-item-description">{{ category.description }}</span>
                </div>
            </div>
        </div>

        <!-- Choices Dropdown -->
        <div
            v-if="isChoicesDropdownVisible()"
            class="BigFilter__filteringDropdown"
        >
            <div class="text-sm font-semibold text-gray-800 h-8 leading-none">
                <Icon
                    v-if="selectedCategory.icon"
                    :name="selectedCategory.icon"
                    size="20px"
                />
                {{ selectedCategory.label }}
            </div>

            <VueFuse
                class="mb-2"
                :defaultAll="true"
                :keys="['label']"
                :list="selectedCategory.choices"
                :placeholder="$t('search')"
                :threshold="0.1"
                @result="onChoiceFuseResult"
            />

            <div
                v-for="choice in filteredCategoryChoices"
                class="menu-item"
                :class="{
                    disabled: isValueDisabled(choice.value),
                }"
                @click.prevent="selectCategoryChoice(choice)"
            >
                <span>{{ choice.label }}</span>
                <span v-if="isValueDisabled(choice.value)">( {{ $t("alreadyUsed") }} )</span>
            </div>

            <div
                v-if="filteredCategoryChoices.length == 0"
                class="content"
            >
                {{ $t("noValue") }}
            </div>
        </div>

        <!-- Calendar Dropdown -->
        <div
            v-if="isCalendarDropdownVisible()"
            class="BigFilter__filteringDropdown"
        >
            <div class="flex">
                <DatePicker
                    :formatWithoutTime="true"
                    :inline="true"
                    @input="selectDate"
                />
            </div>
        </div>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import moment from "moment"
import { $http } from "@js/ajax"
import { parseQueryString } from "@js/queryString"
import Popper from "popper.js"
import PilotMixin from "@components/PilotMixin"
import SavedFilterBigFilterSaveButton from "@views/savedFilters/SavedFilterBigFilterSaveButton.vue"

class FilterItem {
    constructor(category, value, label) {
        this.category = category
        this.name = category.name
        this.value = value
        this.label = label
    }
}

const DATE_LABEL_FORMAT = "DD/MM/YYYY"
const FREE_SEARCH_NAME = "q"
const freeSearchCategory = {
    name: FREE_SEARCH_NAME,
    label: "Recherche",
    multiple: true,
    type: "search",
    icon: "Search",
}

export default {
    name: "BigFilter",
    mixins: [PilotMixin],
    props: {
        // Url of the filter schema
        filterSchemaUrl: {
            type: String,
            required: true,
        },
        // The text to display when no filter is selected
        placeholder: {
            type: String,
            default() {
                return this.$t("search")
            },
        },
        apiSource: {},
        canSave: {
            type: Boolean,
            default: false,
        },
    },
    components: {
        SavedFilterBigFilterSaveButton,
    },
    data: () => ({
        // The schema describing all possible categories and their value choices
        filterSchema: [],
        // The selected filter items
        filterItems: [],

        // The current text into the filter input
        filterInputValue: "",
        // When the search input gain focus
        searchInputFocused: false,
        // The category selected through the dropdown or filter input
        selectedCategory: null,
        // When the user is editing an existing filter item
        editedFilterItemIndex: null,
        // is the filter input currently focused ?
        isFilteringDropdownVisible: false,
        // THe category choices filtered by the Fuse input
        filteredCategoryChoices: [],
        // The PopperJS object that contains the filtering dropdown
        filteringDropdownPopperJS: null,
    }),
    computed: {
        queryString() {
            return this.apiSource.queryString
        },
        filterSchemaByName() {
            return _.keyBy(this.filterSchema, (categorySpec) => categorySpec.name)
        },
        // The values that we already filter on, for the current selectedCategory
        alreadySelectedCategories() {
            return this.filterItems.map((item) => item.category)
        },
        // The values that we already filter on, for the current selectedCategory
        alreadySelectedValues() {
            return this.filterItems
                .filter((item) => item.category == this.selectedCategory)
                .map((item) => item.value)
        },
    },
    methods: {
        /***********************
         * Filter items manipulation
         ************************/
        applyChanges() {
            this.apiSource.setFilterItems(this.filterItems)
        },

        addFilterItem(filterItem) {
            this.filterItems.push(filterItem)
            this.applyChanges()
        },

        removeFilterItem(index) {
            this.filterItems = this.filterItems.filter((_, i) => i !== index)
            this.applyChanges()
        },

        replaceFilterItem(index, filterItem) {
            this.filterItems = this.filterItems.map((fi, i) => (i == index ? filterItem : fi))
            this.applyChanges()
        },

        setFilterItemsFromQueryString(queryString) {
            let initialParams = parseQueryString(queryString)
            this.filterItems = []
            for (let categoryName in initialParams) {
                // Is it a free search filter item ?
                if (categoryName == FREE_SEARCH_NAME) {
                    for (let value of initialParams[categoryName]) {
                        this.filterItems.push(new FilterItem(freeSearchCategory, value, value))
                    }
                    continue
                }

                // Is it a category filter item ?
                let category = this.filterSchemaByName[categoryName]
                if (!category) {
                    continue
                }

                for (let value of initialParams[categoryName]) {
                    let label = value
                    if (category.type == "list") {
                        let choice = _.find(category.choices, (choice) => choice.value == value)
                        if (!choice) {
                            continue
                        }
                        label = choice.label
                    }
                    if (category.type == "date") {
                        label = moment(value).format(DATE_LABEL_FORMAT)
                    }

                    this.filterItems.push(new FilterItem(category, value, label))
                }
            }
        },

        /***********************
         * Value selection
         ************************/
        openFilteringDropdown($event, filterItem = null, filterItemIndex = null) {
            // Existing filterItem edition
            if (filterItem) {
                // Cannot update search
                if (filterItem.category.type == "search") {
                    return
                }

                this.editedFilterItemIndex = filterItemIndex
                this.selectedCategory = filterItem.category
            }
            // Create a new filterItem
            else {
                this.selectedCategory = null
                this.editedFilterItemIndex = null
            }

            this.filteringDropdownPopperJS = new Popper(
                $event.currentTarget,
                this.$refs.filteringDropdown,
                {
                    placement: "bottom-start",
                },
            )
            this.isFilteringDropdownVisible = true
            // Prevent the document clik handler to close the dropdown immediately
            $event.stopPropagation()
        },
        closeFilteringDropdown() {
            this.isFilteringDropdownVisible = false
            this.selectedCategory = null
            this.editedFilterItemIndex = null
            if (this.filteringDropdownPopperJS) {
                this.filteringDropdownPopperJS.destroy()
            }
        },
        resetInput() {
            this.filterInputValue = ""
            this.closeFilteringDropdown()
            $(this.$refs.filterInput).blur()
        },
        selectFreeSearch() {
            if (!this.filterInputValue) {
                return
            }
            this.addFilterItem(
                new FilterItem(freeSearchCategory, this.filterInputValue, this.filterInputValue),
            )
            this.resetInput()
        },
        selectCategory(category) {
            // Do nothing if this category were already selected
            if (this.isCategoryDisabled(category)) {
                return
            }

            this.selectedCategory = category
        },
        selectValue(value, label) {
            // Do nothing if this value were already selected
            if (this.isValueDisabled(value)) {
                return
            }

            let filterItem = new FilterItem(this.selectedCategory, value, label)
            if (this.editedFilterItemIndex != null) {
                this.replaceFilterItem(this.editedFilterItemIndex, filterItem)
            } else {
                this.addFilterItem(filterItem)
            }

            this.resetInput()
        },
        selectCategoryChoice(choice) {
            this.selectValue(choice.value, choice.label)
        },
        selectDate(date) {
            this.selectValue(date, moment(date).format(DATE_LABEL_FORMAT))
        },

        onChoiceFuseResult(filteredCategoryChoices) {
            this.filteredCategoryChoices = filteredCategoryChoices
        },
        /***********************
         * Dropdown helpers
         ************************/
        isCategoryDropdownVisible() {
            return this.isFilteringDropdownVisible && !this.selectedCategory
        },
        isChoicesDropdownVisible() {
            return (
                this.isFilteringDropdownVisible &&
                this.selectedCategory &&
                this.selectedCategory.type == "list"
            )
        },
        isCalendarDropdownVisible() {
            return (
                this.isFilteringDropdownVisible &&
                this.selectedCategory &&
                this.selectedCategory.type == "date"
            )
        },
        isCategoryDisabled(category) {
            return !category.multiple && this.alreadySelectedCategories.includes(category)
        },
        isValueDisabled(value) {
            return this.alreadySelectedValues.includes(value)
        },
    },
    watch: {
        queryString() {
            this.setFilterItemsFromQueryString(this.queryString)
        },
    },
    created() {
        $http.get(this.filterSchemaUrl).then((response) => {
            this.filterSchema = response.data
            if (this.queryString) {
                this.setFilterItemsFromQueryString(this.queryString)
            }
        })
    },
    mounted() {
        // Close the dropdown when clicking outside it
        $(document).on("click.BigFilter", (event) => {
            if (
                this.isFilteringDropdownVisible &&
                !this.$refs.filteringDropdown.contains(event.target) &&
                // IE11 does not understands document.contains, we need to use document.body.contains
                document.body.contains(event.target)
            ) {
                this.closeFilteringDropdown()
            }
        })
    },
    beforeDestroy() {
        this.closeFilteringDropdown()
        $(document).off("click.BigFilter")
    },
    i18n: {
        messages: {
            fr: {
                addFilter: "Ajouter un filtre",
                alreadyUsed: "Déjà utilisé",
                filterOrSearch: "Chercher ou filtrer",
                hitEnterToSearchFor: "Cliquez ici ou appuyez sur Entrée pour chercher",
                inTitleOrContent: "dans le titre ou le contenu",
                noValue: "Pas de valeur disponible",
                selectFilter: "Filtres disponibles",
                typeTextToSearch: "Entrer du texte pour rechercher",
            },
            en: {
                addFilter: "Add filter",
                alreadyUsed: "Already in use",
                filterOrSearch: "Search or filter",
                hitEnterToSearchFor: "Click here or press Enter to search",
                inTitleOrContent: "in title or content",
                noValue: "No value",
                selectFilter: "Available filters",
                typeTextToSearch: "Type text to search",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.BigFilter {
    @apply flex flex-wrap items-center w-full;
}

.BigFilter__filterItem {
    @apply inline-flex items-center rounded-sm;
    @apply my-1 mr-1 px-3 py-2;
    @apply border border-blue-200;
    @apply text-xs leading-4 font-medium;
    @apply text-blue-700 bg-blue-100;
    @apply max-w-xs;

    &:hover {
        @apply bg-blue-50;
    }
}

.BigFilter__filterItemDescription {
    @apply flex items-center font-semibold pl-2 pr-1 truncate cursor-pointer;

    &:hover,
    &:focus {
        @apply bg-blue-200;
    }
}

.BigFilter__searchInput {
    @apply flex-grow rounded-sm rounded-l-none border border-gray-200 border-l-0 bg-gray-50 bg-white pl-3 w-full;
    height: 38px;
}

%BigFilter__dropdown {
    @media (max-height: 550px) {
        max-height: 250px;
    }
    @media (min-height: 550px) and (max-height: 650px) {
        max-height: 350px;
    }
    @media (min-height: 650px) and (max-height: 750px) {
        max-height: 450px;
    }
    @media (min-height: 750px) {
        max-height: 550px;
    }
}

.BigFilter__searchHintDropdown {
    @extend %BigFilter__dropdown;

    @apply absolute w-64;
    @apply bg-white shadow;
    @apply text-gray-600 p-3;
    top: 100%;
    z-index: 30;
}

.BigFilter__filteringDropdown {
    @extend %BigFilter__dropdown;

    @apply pr-4 overflow-x-hidden overflow-y-auto;
    min-width: 300px;
}
</style>
