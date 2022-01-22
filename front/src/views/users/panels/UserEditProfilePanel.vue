<template>
<OffPanel
    name="UserEditProfilePanel"
    :stretched="true"
    @opened="onOpen"
>
    <div slot="offPanelTitle">{{ $t("myAccount") }}</div>
    <div
        class="flex flex-col flex-auto"
        slot="offPanelBody"
    >
        <BaseForm
            :disableSave="disableSave"
            :model="model"
            :partialSave="true"
            :saveUrl="urls.usersMe"
            :stretched="true"
            :vuelidate="$v.model"
            @cancel="closeOffPanel('UserEditProfilePanel')"
            @saved="onUserSaved"
        >
            <template #default>
                <FormField
                    :schema="{
                        type: 'char',
                        label: $t('username'),
                    }"
                    v-model.trim="model.username"
                    :vuelidate="$v.model.username"
                />

                <FormField
                    :schema="{
                        type: 'email',
                        label: $t('email'),
                    }"
                    v-model.trim="model.email"
                    :vuelidate="$v.model.email"
                />

                <FormField
                    :schema="{
                        type: 'char',
                        label: $t('firstName'),
                    }"
                    v-model.trim="model.first_name"
                    :vuelidate="$v.model.first_name"
                />

                <FormField
                    :schema="{
                        type: 'char',
                        label: $t('lastName'),
                    }"
                    v-model.trim="model.last_name"
                    :vuelidate="$v.model.last_name"
                />

                <FileField
                    ref="avatar"
                    :acceptUrl="urls.usersS3SignatureForAvatar"
                    :buttonText="$t('uploadAvatar')"
                    :currentFile="me.avatar"
                    :height="100"
                    :label="$t('avatar')"
                    :width="100"
                    @input="onAvatarInput"
                />

                <FormField
                    v-model="model.language"
                    :schema="{
                        type: 'choice',
                        label: $t('language'),
                        choices: UILanguages,
                    }"
                    :vuelidate="$v.model.language"
                />

                <FormField
                    v-model="model.timezone"
                    :schema="{
                        type: 'choice',
                        label: $t('timezone'),
                        choices: timezones,
                    }"
                    :vuelidate="$v.model.timezone"
                />

                <FormField
                    v-model="model.login_menu"
                    :schema="{
                        type: 'choice',
                        label: $t('loginMenu'),
                        choices: loginMenus,
                    }"
                    :vuelidate="$v.model.login_menu"
                />

                <FormField
                    :schema="{
                        type: 'char',
                        label: $t('phone'),
                    }"
                    v-model.trim="model.phone"
                    :vuelidate="$v.model.phone"
                />

                <FormField
                    :schema="{
                        type: 'char',
                        label: $t('localization'),
                    }"
                    v-model.trim="model.localization"
                    :vuelidate="$v.model.localization"
                />

                <FormField
                    :schema="{
                        type: 'char',
                        label: $t('job'),
                    }"
                    v-model.trim="model.job"
                    :vuelidate="$v.model.job"
                />
            </template>
        </BaseForm>
    </div>
</OffPanel>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { required, email } from "vuelidate/lib/validators"
import { setCurrentLocale } from "@js/localize"
import PilotMixin from "@components/PilotMixin"

import FileField from "@components/forms/widgets/FileField"

export default {
    name: "UserEditProfilePanel",
    mixins: [PilotMixin],
    components: {
        FileField,
    },
    data: () => ({
        model: {
            id: null,
            username: "",
            email: "",
            first_name: "",
            last_name: "",
            avatar: null,
            language: "",
            timezone: "",
            login_menu: "",
            phone: "",
            localization: "",
            job: "",
        },
        // Clone to prevent memory leak incurred by a top-level reactive object.
        UILanguages: _.cloneDeep(window.pilot.UILanguages),
        timezones: _.cloneDeep(window.pilot.timezones),
        loginMenus: _.cloneDeep(window.pilot.loginMenus),
    }),
    validations: {
        model: {
            username: { required },
            email: { required, email },
        },
    },
    computed: {
        ...mapState("users", ["me"]),
        disableSave() {
            return this.$refs.avatar && this.$refs.avatar.uploadInProgress
        },
    },
    methods: {
        ...mapMutations("users", ["setUserMe"]),
        ...mapMutations("offPanel", ["closeOffPanel"]),
        onOpen() {
            this.model = _.pick(this.me, [
                "id",
                "username",
                "email",
                "first_name",
                "last_name",
                "language",
                "timezone",
                "login_menu",
                "phone",
                "localization",
                "job",
            ])
        },
        onAvatarInput(avatar) {
            this.model.avatar = avatar
            this.$v.model.$touch()
        },
        onUserSaved(user) {
            this.setUserMe(user)
            // Update the UI language if the user changed his preference
            setCurrentLocale(user.language, this.$root)
            this.$refs.avatar.reset()
            setTimeout(() => this.closeOffPanel("UserEditProfilePanel"), 2000)
        },
    },
    i18n: {
        messages: {
            fr: {
                avatar: "Avatar",
                firstName: "Prénom",
                lastName: "Nom",
                job: "Métier",
                localization: "Localisation",
                loginMenu: "Menu de connexion",
                phone: "Téléphone",
                timezone: "Fuseau horaire",
                username: "Nom d'utilisateur",
                uploadAvatar: "Envoyer un avatar pour votre utilisateur",
            },
            en: {
                avatar: "Avatar",
                firstName: "First name",
                lastName: "Last name",
                job: "Position",
                localization: "Place",
                loginMenu: "Landing after login",
                phone: "Phone",
                timezone: "Timezone",
                username: "Username",
                uploadAvatar: "Upload avatar for your user",
            },
        },
    },
}
</script>
