<template>
<div class="SearchResult">
    <div>
        <SmartLink
            class="SearchResult__Title"
            :to="item._source.url"
        >
            #{{ item._source.id }}
            <span
                v-if="highlight.title"
                v-html="highlight.title[0]"
                class="SearchResult__highlight"
            ></span>
            <span v-else>{{ item._source.title }}</span>
        </SmartLink>
    </div>

    <div
        v-if="highlight.content"
        class="SearchResult__ContentHits"
    >
        <div
            v-for="contentHighlight in highlight.content"
            class="ContentHit"
        >
            ..
            <span
                v-html="contentHighlight"
                class="SearchResult__highlight"
            ></span>
            ..
        </div>
    </div>

    <div class="SearchResult__InfosList">
        <div class="Info">
            <span class="Info__key">{{ $t("project") }}:</span>
            <span
                v-if="!item._source.project"
                class="Info__value"
            >
                {{ $t("none") }}
            </span>
            <span
                v-else
                v-html="formatField('project')"
                class="Info__value"
            />
        </div>
        <div class="Info">
            <span class="Info__key">{{ $t("channels") }}:</span>
            <span
                v-if="!item._source.channels.length"
                class="Info__value"
            >
                {{ $t("none") }}
            </span>
            <span
                v-else
                v-html="formatField('channels', ', ')"
                class="Info__value"
            />
        </div>
        <div class="Info">
            <span class="Info__key">{{ $t("publicationDate") }}:</span>
            <span
                v-if="!item._source.publication_dt"
                class="Info__value"
            >
                {{ $t("none") }}
            </span>
            <span
                v-else
                class="Info__value"
            >
                {{ item._source.publication_dt | dateFormat }}
            </span>
        </div>
        <div class="Info">
            <span class="Info__key">{{ $t("targets") }}:</span>
            <span
                v-if="!item._source.targets.length"
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
                v-if="!item._source.tags.length"
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
        <div class="Info">
            <span class="Info__key">{{ $t("language") }}:</span>
            <span
                v-if="!item._source.language"
                class="Info__value"
            >
                {{ $t("none") }}
            </span>
            <span
                v-else
                v-html="formatField('language')"
                class="Info__value"
            />
        </div>
    </div>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "SearchItemHitDisplay",
    mixins: [PilotMixin],
    props: {
        searchHit: Object,
    },
    computed: {
        item() {
            return this.searchHit
        },
        highlight() {
            return this.item.highlight || {}
        },
    },
    methods: {
        formatField(fieldName, joinWith = "") {
            let fieldValue = this.item._source[fieldName],
                fieldHighlight = this.highlight[fieldName]

            if (fieldValue instanceof Array) {
                if (fieldHighlight && fieldHighlight.length) return fieldHighlight.join(joinWith)
                else return fieldValue.join(joinWith)
            } else {
                if (fieldHighlight) return fieldHighlight[0]
                else return fieldValue
            }
        },
    },
}
</script>
