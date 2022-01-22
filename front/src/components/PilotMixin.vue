<script>
/**
 *  Group all base components and store mappings to avoid boilerplate.
 *  To prevent cyclical import, don't use it on the components imported here,
 *  and don't import <FullLayout> here.
 */

import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import colors from "@sass/colors.scss"
import urls from "@js/urls"

import AutoForm from "@components/forms/AutoForm"
import AutoFormInPanel from "@components/forms/AutoFormInPanel"
import BaseForm from "@components/forms/BaseForm.vue"
import { BarLoader } from "@saeris/vue-spinners"
import DatePicker from "@components/forms/widgets/DatePicker"
import DatePickerPopper from "@components/picker/DatePickerPopper"
import Deletarium from "@components/Deletarium.vue"
import FormField from "@components/forms/FormField"
import Icon from "@components/Icon.vue"
import Loadarium from "@components/Loadarium.vue"
import Loading from "@components/Loading.vue"
import OffPanel from "@components/OffPanel.vue"
import Popper from "@components/Popper.vue"
import RichTextInput from "@components/forms/widgets/RichTextInput.vue"
import SelectInput from "@components/forms/widgets/SelectInput"
import SmartButtonSpinner from "@components/SmartButtonSpinner.vue"
import SmartLink from "@components/SmartLink.vue"
import Spinner from "@components/Spinner.vue"
import TextAreaAutosize from "@components/forms/widgets/TextAreaAutosize.vue"
import UserAvatar from "@views/users/UserAvatar.vue"
import UserDisplay from "@views/users/UserDisplay.vue"
import ValidationErrors from "@components/forms/ValidationErrors.vue"
import ValidationWarnings from "@components/forms/ValidationWarnings.vue"
import VueFuse from "@components/VueFuse.vue"

export default {
    name: "PilotMixin",
    props: {
        namespace: String,
    },
    components: {
        AutoForm,
        AutoFormInPanel,
        BaseForm,
        BarLoader,
        DatePicker,
        DatePickerPopper,
        Deletarium,
        FormField,
        Icon,
        Loadarium,
        Loading,
        OffPanel,
        Popper,
        RichTextInput,
        SelectInput,
        SmartButtonSpinner,
        SmartLink,
        Spinner,
        TextAreaAutosize,
        UserAvatar,
        UserDisplay,
        ValidationErrors,
        ValidationWarnings,
        VueFuse,
    },
    data: () => ({
        colors,
        urls,
    }),
    computed: {
        ...mapGetters(["currentRouteName"]),
        ...mapState(["contentTypes", "currentDesk"]),
    },
    methods: {
        ...mapMutations("offPanel", ["openOffPanel", "closeOffPanel"]),
    },
}
</script>
