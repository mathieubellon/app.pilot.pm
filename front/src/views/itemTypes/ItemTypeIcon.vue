<!--
PLEASE read doc in IconMixin.vue
-->

<script>
import IconMixin from "@components/IconMixin"

import Cloud from "@svg/item_type_icons/cloud.svg"
import Drupal from "@svg/item_type_icons/drupal.svg"
import Email from "@svg/item_type_icons/email.svg"
import Facebook from "@svg/item_type_icons/facebook.svg"
import File from "@svg/item_type_icons/file.svg"
import Instagram from "@svg/item_type_icons/instagram.svg"
import Linkedin from "@svg/item_type_icons/linkedin.svg"
import Messages from "@svg/item_type_icons/messages.svg"
import Podcast from "@svg/item_type_icons/podcast.svg"
import Snapchat from "@svg/item_type_icons/snapchat.svg"
import Sound from "@svg/item_type_icons/sound.svg"
import Twitter from "@svg/item_type_icons/twitter.svg"
import Videoclip from "@svg/item_type_icons/videoclip.svg"
import Vimeo from "@svg/item_type_icons/vimeo.svg"
import Yammer from "@svg/item_type_icons/yammer.svg"
import Youtube from "@svg/item_type_icons/youtube.svg"

const ITEM_TYPE_ICONS = {
    Cloud,
    Drupal,
    Email,
    Facebook,
    File,
    Instagram,
    Linkedin,
    Messages,
    Podcast,
    Snapchat,
    Sound,
    Twitter,
    Videoclip,
    Vimeo,
    Yammer,
    Youtube,
}

export default {
    name: "ItemTypeIcon",
    mixins: [IconMixin],
    data: () => ({
        icons: ITEM_TYPE_ICONS,
        defaultIcon: File,
    }),
}

export { ITEM_TYPE_ICONS }
</script>
