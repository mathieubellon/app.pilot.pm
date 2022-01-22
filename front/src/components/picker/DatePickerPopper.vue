<template>
<Popper
    closeOnClickSelector=".CloseDatePickerPopper"
    :placement="placement"
    :triggerElementName="triggerElementName"
    triggerType="click"
    :visibleArrow="false"
>
    <template #triggerElement>
        <slot name="triggerElement" />
    </template>

    <template #content>
        <div style="width: 315px">
            <div class="py-3 flex flex-col justify-center">
                <slot name="message" />
            </div>

            <div class="flex flex-col items-center">
                <DatePicker
                    :formatWithoutTime="formatWithoutTime"
                    :hideInput="true"
                    :inline="true"
                    :naiveTime="naiveTime"
                    :value="value"
                    @input="$emit('input', $event)"
                />
                <div class="mt-5 flex items-center justify-between w-full">
                    <a
                        class="button is-red"
                        @click="$emit('input', null)"
                    >
                        {{ $t("remove") }}
                    </a>
                    <a class="button CloseDatePickerPopper">
                        {{ $t("close") }}
                    </a>
                </div>
            </div>
        </div>
    </template>
</Popper>
</template>

<script>
import DatePicker from "@components/forms/widgets/DatePicker"
import Popper from "@components/Popper.vue"

export default {
    name: "DatePickerPopper",
    components: {
        DatePicker,
        Popper,
    },
    props: {
        value: String,
        formatWithoutTime: Boolean,
        naiveTime: Boolean,
        placement: {
            type: String,
            default: "bottom",
        },
        triggerElementName: {
            type: String,
            required: true,
        },
    },
    i18n: {
        messages: {
            fr: {
                deleteDate: "Cliquez ici pour la supprimer",
            },
            en: {
                deleteDate: "Click here to delete it",
            },
        },
    },
}
</script>
