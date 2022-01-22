<template>
<div
    class="ProjectListElement"
    :class="{
        isOpenedProgressBar: isOpenedProgressBar,
        isRejected: project.state === 'rejected',
        isCopying: project.state === 'copy',
    }"
    ref="project"
>
    <div class="px-4">
        <Icon
            v-if="project.state === 'closed'"
            name="ProjectClosed"
            size="20px"
        />
        <Icon
            v-else-if="project.state === 'idea'"
            name="ProjectSuggested"
            size="20px"
        />
        <Icon
            v-else-if="project.state === 'rejected'"
            name="ProjectRejected"
            size="20px"
        />
        <Icon
            v-else
            name="Project"
            size="20px"
        />
    </div>

    <div class="flex flex-grow flex-col truncate">
        <div
            v-if="project.state === 'copy'"
            class="Project__title"
        >
            {{ project.name }}
        </div>
        <SmartLink
            v-else
            class="Project__title"
            :to="project.url"
        >
            {{ project.name }}
        </SmartLink>
        <div class="flex items-center text-sm font-medium text-gray-500">
            #{{ project.id }}&nbsp;&bull;&nbsp;
            <div v-if="isIdeaProject">
                <span v-if="project.created_by_external_email">
                    {{ $t("suggestedBy") }} {{ project.created_by_external_email }}
                </span>
                <span v-else>
                    {{ $t("createdBy") }}
                    <UserDisplay :user="project.created_by" />
                </span>
                <span>{{ $t("at") }} {{ project.created_at | dateFormat }}</span>
                &bull;&nbsp;&nbsp;&nbsp;
            </div>
            <span
                v-if="project.start"
                class="Project__startDate"
            >
                {{ project.start | dateFormat }}
            </span>
            <span
                v-else
                class="Project__startDate"
            >
                ?
            </span>
            &nbsp;&#8594;&nbsp;
            <span
                v-if="project.end"
                class="Project__endDate"
            >
                {{ project.end | dateFormat }}
            </span>
            <span
                v-else
                class="Project__endDate"
            >
                ?
            </span>
            &nbsp;&bull;&nbsp;
            <a
                v-if="project.progress.length > 0"
                class="text-blue-400 text-underline"
                @click="toggleProgressBar"
            >
                {{ $t("progression") }}
            </a>
            <div
                v-else
                class="text-gray-500"
            >
                {{ $t("noContent") }}
            </div>
            <template v-if="project.category">&nbsp;&bull;&nbsp;</template>
            <Label
                :goToListOnClick="true"
                :label="project.category"
            />
        </div>
        <p
            v-if="project.search_headline"
            v-html="project.search_headline"
            class="Project__searchHeadline"
        />
        <div v-if="project.state === 'copy'">
            {{ $t("copyInProgress") }}
        </div>
        <div v-else-if="project.state === 'rejected'">
            {{ $t("suggestionRejected") }}
        </div>
        <transition
            enter-active-class="animated fadeInDown"
            leave-active-class="animated fadeOutUp"
        >
            <div
                v-if="isOpenedProgressBar"
                class="Project__progress__full mt-2"
            >
                <div
                    v-for="state in project.progress"
                    class="Project__progress__status isOpenedProgressBar rounded"
                    :style="{ 'background-color': state.color, 'flex-grow': state.occurences }"
                    :key="state.label"
                >
                    <div class="progressText">{{ state.label }} ({{ state.occurences }})</div>
                </div>
            </div>
        </transition>
    </div>
    <div
        v-if="project.priority"
        class="w-40 flex-shrink-0 px-4"
    >
        <Label
            class="text-xs"
            :goToListOnClick="true"
            :label="project.priority"
        />
    </div>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

import Label from "@views/labels/Label.vue"
import UserDisplay from "@views/users/UserDisplay"

export default {
    name: "ProjectListElement",
    mixins: [PilotMixin],
    components: {
        Label,
        UserDisplay,
    },
    props: {
        project: {
            type: Object,
            required: true,
        },
    },
    data: () => ({
        isOpenedProgressBar: false,
    }),
    computed: {
        isIdeaProject() {
            return this.$route && this.$route.name == "projectList-idea"
        },
    },
    methods: {
        toggleProgressBar() {
            if (this.project.progress.length > 0) {
                this.isOpenedProgressBar = !this.isOpenedProgressBar
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                copyInProgress: "Copie en cours",
                progression: "Voir progression",
            },
            en: {
                copyInProgress: "Copy in progress",
                progression: "Show progress",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.ProjectListElement {
    @apply mb-2 w-full flex flex-grow w-full bg-white rounded border border-gray-300 items-center py-5;
}

.ProjectListElement.isCopying {
    color: #607d8b;
    background-color: #cfd8dc;
}

/*
.Project {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #fff;
    border-radius: 3px;
    margin-top: 0.5em;
    padding: 1em;
    flex-grow: 1;
    z-index: 21;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);

    .button {
        margin: 0;
    }

    @media screen and(max-width: 1000px) {
        flex-direction: column;
    }
}

.Project.isRejected {
    color: #607d8b;
    background-color: #cfd8dc;

    .Project__infos {
        text-decoration: line-through;
    }

    .Project__progress {
        display: none;
    }
}

.Project.isOpenedProgressBar {
    border-left: 1px solid #cfd8dc;
    border-right: 1px solid #cfd8dc;
    border-top: 1px solid #cfd8dc;
    border-bottom: none;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    box-shadow: 0 3px 13px 0px rgba(0, 0, 0, 0.34);
}

 */

.Project__infos {
    display: flex;
    flex-shrink: 1; /* do not shrink - initial value: 1 */
    flex-grow: 1;
    width: 100%;
    flex-direction: column;
    margin-left: 0.8em;
}

.Project__title {
    @apply text-gray-900 text-base font-semibold;

    &:hover {
        @apply text-blue-700 underline;
    }
}

.Project__subtitle {
    font-size: 0.9em;
    color: #607d8b;
    margin-bottom: 0.3em;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    @media screen and(max-width: 1000px) {
        justify-content: left;
    }

    @mixin Project__subtitle__elt {
        margin-right: 1em;
    }

    .Project__id {
        @include Project__subtitle__elt();
    }

    .Project__createdBy {
        @include Project__subtitle__elt();
    }

    .Project__startDate {
        @include Project__subtitle__elt();
    }

    .Project__endDate {
        @include Project__subtitle__elt();
    }
}

.Project__subtitle__infoLabel {
    color: #90a4ae;
}

.Project__searchHeadline {
    font-size: 0.9em;

    .highlight {
        background: #ffff00;
        font-weight: bold;
    }
}

// /////////////////////////
// Progress
// /////////////////////////

.Project__progress {
    display: flex;
    flex-direction: column;
    //flex-shrink: 0; /* do not shrink - initial value: 1 */
    //flex-basis: 10em; /* width/height  - initial value: auto */
    margin-right: 1em;
    margin-left: 2em;
    cursor: pointer;
    width: 100%;
    // background-color: aquamarine;
    padding-bottom: 1em;
    @media screen and(max-width: 1000px) {
        //        width: 100%;
        //      margin-right: 0;
        //    flex-basis: auto;
    }
}

.Project__progress__statuses {
    display: flex;
    align-items: center;
}

.Project__progress__full {
    display: flex;
    z-index: 20;
    border-left: 1px solid #cfd8dc;
    border-right: 1px solid #cfd8dc;
    border-bottom: 1px solid #cfd8dc;
    border-bottom-left-radius: 3px;
    border-bottom-right-radius: 3px;
}

.Project__progress__status.isOpenedProgressBar {
    height: 2em;
}

.Project__progress__status {
    height: 7px;
}

.Project__progress__status:first-child {
    border-top-left-radius: 3px;
    border-bottom-left-radius: 3px;
}

.Project__progress__status.isOpenedProgressBar:first-child {
    border-radius: 0;
}

.Project__progress__status:last-child {
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
}

.Project__progress__status.isOpenedProgressBar:last-child {
    border-radius: 0;
}

.progressText {
    color: #fff;
    align-items: center;
    display: flex;
    justify-content: center;
    height: 100%;
}

.Project__progress__title {
    font-size: 0.8em;
    color: #b0bec5;
    @media screen and(max-width: 800px) {
        text-align: center;
    }
}
</style>
