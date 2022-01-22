<template>
<div class="SearchResult">
    <div>
        <SmartLink
            class="SearchResult__Title"
            :to="project._source.url"
        >
            #{{ project._source.id }}
            <span
                v-if="highlight.name"
                v-html="highlight.name[0]"
                class="SearchResult__highlight"
            ></span>
            <span v-else>{{ project._source.name }}</span>
        </SmartLink>
    </div>

    <div
        v-if="highlight.description"
        class="SearchResult__ContentHits"
    >
        <div
            v-for="descriptionHighlight in highlight.description"
            class="ContentHit"
        >
            [..]
            <span
                v-html="descriptionHighlight"
                class="SearchResult__highlight"
            ></span>
            [..]
        </div>
    </div>

    <div class="SearchResult__InfosList">
        <div class="Info">
            <span class="Info__key">{{ $t("channels") }}:</span>
            <span
                v-if="!project._source.channels.length"
                class="Info__value"
            >
                {{ $t("none") }}
            </span>
            <span
                v-else
                v-html="formatField('channels', ' / ')"
                class="Info__value"
            />
        </div>
        <div class="Info">
            <span class="Info__key">{{ $t("targets") }}:</span>
            <span
                v-if="!project._source.targets.length"
                class="Info__value"
            >
                {{ $t("none") }}
            </span>
            <span
                v-else
                v-html="formatField('targets', ' / ')"
                class="Info__value"
            />
        </div>
        <div class="Info">
            <span class="Info__key">Tags:</span>
            <span
                v-if="!project._source.tags.length"
                class="Info__value"
            >
                {{ $t("none") }}
            </span>
            <span
                v-else
                v-html="formatField('tags', ', ')"
                class="Info__value"
            />
        </div>
    </div>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "SearchProjectHitDisplay",
    mixins: [PilotMixin],
    props: {
        searchHit: Object,
    },
    computed: {
        project() {
            return this.searchHit
        },
        highlight() {
            return this.project.highlight || {}
        },
    },
    methods: {
        formatField(fieldName, joinWith = "") {
            let fieldValue = this.project._source[fieldName],
                fieldHighlight = this.highlight[fieldName]

            if (fieldHighlight && fieldHighlight.length) return fieldHighlight.join(joinWith)
            else return fieldValue.join(joinWith)
        },
    },
}
</script>
