<!--
PLEASE read doc in IconMixin.vue
-->

<script>
import IconMixin from "@components/IconMixin"

import asset from "@svg/item_content_field_icons/asset.svg"
import auto_complete from "@svg/item_content_field_icons/auto_complete.svg"
import char from "@svg/item_content_field_icons/char.svg"
import choice from "@svg/item_content_field_icons/choice.svg"
import email from "@svg/item_content_field_icons/email.svg"
import facebook from "@svg/item_content_field_icons/facebook.svg"
import help_text from "@svg/item_content_field_icons/help_text.svg"
import integer from "@svg/item_content_field_icons/integer.svg"
import multi_checkboxes from "@svg/item_content_field_icons/multi_checkboxes.svg"
import prosemirror from "@svg/item_content_field_icons/richtext.svg"
import radio from "@svg/item_content_field_icons/radio.svg"
import text from "@svg/item_content_field_icons/text.svg"
import twitter from "@svg/item_content_field_icons/twitter.svg"

const ITEM_CONTENT_FIELD_ICONS = {
    asset,
    auto_complete,
    char,
    choice,
    email,
    facebook,
    help_text,
    integer,
    multi_checkboxes,
    prosemirror,
    radio,
    text,
    twitter,
}

export default {
    name: "ItemContentFieldIcon",
    mixins: [IconMixin],
    data: () => ({
        icons: ITEM_CONTENT_FIELD_ICONS,
    }),
}
</script>
