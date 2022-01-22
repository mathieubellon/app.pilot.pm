<template>
<Popper triggerElementName="PopperRef">
    <template #triggerElement>
        <!-- .stop needed on @click to prevent version loading -->
        <button
            class="menu-item"
            ref="PopperRef"
        >
            {{ $t("export") }}
        </button>
    </template>

    <template #content>
        <!-- .stop needed on @click to prevent version loading -->
        <a
            class="menu-item"
            :href="getExportUrl('plaintext')"
        >
            {{ $t("text") }}
        </a>
        <a
            class="menu-item"
            :href="getExportUrl('html')"
        >
            HTML
        </a>
        <a
            class="menu-item"
            :href="getExportUrl('pdf')"
        >
            PDF
        </a>
        <a
            class="menu-item"
            :href="getExportUrl('docx')"
        >
            MS Word (.docx)
        </a>
    </template>
</Popper>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import urls from "@js/urls"
import Popper from "@components/Popper.vue"

export default {
    name: "ItemExportDropdown",
    components: {
        Popper,
    },
    props: {
        sessionId: {
            type: Number,
            required: false,
        },
    },
    computed: {
        ...mapGetters("itemDetail", ["itemId"]),
    },
    methods: {
        getExportUrl(format) {
            let url = urls.itemExport.format({ id: this.itemId }) + "?type=" + format
            if (this.sessionId) {
                url += "&session=" + this.sessionId
            }
            return url
        },
    },
    i18n: {
        messages: {
            fr: {
                export: "Exporter",
                text: "Texte",
            },
            en: {
                export: "Export",
                text: "Text",
            },
        },
    },
}
</script>
