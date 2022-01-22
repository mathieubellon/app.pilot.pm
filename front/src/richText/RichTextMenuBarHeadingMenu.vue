<template>
<div class="flex flex-col">
    <RichTextMenuBarItem
        name="paragraph"
        :inDropdown="true"
        :label="$t('paragraph')"
    />

    <template v-for="hIndex in 6">
        <RichTextMenuBarItem
            :class="'heading' + hIndex"
            name="heading"
            :attrs="{ level: hIndex }"
            :inDropdown="true"
            :label="`${$t('heading')} ${hIndex}`"
            :showIcon="false"
        />
    </template>
</div>
</template>

<script>
import RichTextMenuBarItem from "./RichTextMenuBarItem"

export default {
    name: "RichTextMenuBarHeadingMenu",
    components: {
        RichTextMenuBarItem,
    },
    i18n: {
        messages: {
            fr: {
                heading: "Titre",
                paragraph: "Texte normal",
            },
            en: {
                heading: "Heading",
                paragraph: "Normal text",
            },
        },
    },
}
</script>
