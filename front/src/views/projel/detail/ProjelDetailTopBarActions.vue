<template>
<Fragment>
    <Popper
        closeOnClickSelector=".willClose"
        triggerElementName="PopperRef"
        triggerType="click"
    >
        <template #triggerElement>
            <button
                class="button is-topbar"
                ref="PopperRef"
            >
                {{ $t("actions") }}
                <!-- The empty span is required to correctly align with flex display -->
                <span>
                    <Icon
                        class="caret"
                        name="ChevronDown"
                    />
                </span>
            </button>
        </template>

        <template #content>
            <ProjelDetailOptions />
        </template>
    </Popper>
</Fragment>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import { Fragment } from "vue-fragment"

import ProjelDetailOptions from "./ProjelDetailOptions"

export default {
    name: "ProjelDetailTopBarActions",
    mixins: [PilotMixin],
    components: {
        Fragment,
        ProjelDetailOptions,
    },
}
</script>
