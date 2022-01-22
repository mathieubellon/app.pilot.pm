<template>
<div class="ActivityFieldDiff">
    <span class="font-semibold">{{ fieldDiff.field_label }}</span>
    :

    <SmartLink
        v-if="isItemContentDiff"
        :to="activity.action_object.details.url"
    >
        {{ $t("seeDiffOnItemPage") }}
    </SmartLink>
    <span
        v-else
        v-html="htmlDiff"
    />
</div>
</template>

<script>
import _ from "lodash"
import PilotMixin from "@components/PilotMixin"
import { dateFormat, yesno } from "@js/filters"
import { formatDiff, textDiff } from "@js/diff/textDiff"

export default {
    name: "ActivityFieldDiff",
    mixins: [PilotMixin],
    props: {
        activity: Object,
        fieldDiff: Object,
    },
    computed: {
        isItemContentDiff() {
            return this.fieldDiff.field_name == "json_content"
        },
        htmlDiff() {
            let fieldType = this.fieldDiff.field_type,
                before = this.fieldDiff.before,
                after = this.fieldDiff.after,
                result = ""

            // Special handling for m2m
            if (fieldType == "ManyToManyField") {
                let m2mDiff = []

                for (let value of _.differenceWith(before, after, _.isEqual)) {
                    m2mDiff.push(`- <del>${value.repr}</del>`)
                }
                for (let value of _.differenceWith(after, before, _.isEqual)) {
                    m2mDiff.push(`+ <ins>${value.repr}</ins>`)
                }

                return m2mDiff.join("<br />")
            }

            // For ForeignKey, retrieve the representation of the related instance
            else if (fieldType == "ForeignKey") {
                // In the case of a migration which changed the field to/from ForeignKey,
                // the before/after version won't be related object
                if (before.hasOwnProperty("repr")) before = before.repr
                if (after.hasOwnProperty("repr")) after = after.repr
            }

            // CharFields and TextFields are handled by diff match patch
            else if (fieldType == "CharField" || fieldType == "TextField") {
                result = formatDiff(textDiff(before, after))
            }

            // Ignore time in DateTimeField, its never actually used by the end-user
            else if (fieldType == "DateField" || fieldType == "DateTimeField") {
                before = before ? dateFormat(before) : ""
                after = after ? dateFormat(after) : ""
            } else if (fieldType == "BooleanField") {
                before = yesno(before)
                after = yesno(after)
            } else if (fieldType == "JSONField") {
                if (before) {
                    before = "[Texte]"
                }
                if (after) {
                    after = "[Texte]"
                }
            }

            // Standard handling for other fields
            if (!result) {
                result = `<del>${before || "∅"}</del> -> <ins>${after || "∅"}</ins>`
            }

            return result
        },
    },
    i18n: {
        messages: {
            fr: {
                seeDiffOnItemPage: "Voir le détail sur la page Contenu",
            },
            en: {
                seeDiffOnItemPage: "See details on the Content page",
            },
        },
    },
}
</script>
