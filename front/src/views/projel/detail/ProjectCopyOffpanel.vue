<template>
<OffPanel
    class="ProjectCopyOffpanel"
    name="copyProject"
    @opened="onOpen"
>
    <div slot="offPanelTitle">{{ $t("copyProject") }}</div>
    <div slot="offPanelBody">
        <template v-if="copyStarted">
            <p>{{ $t("copyProjectSuccess") }}</p>
            <SmartLink
                class="button expanded"
                :to="urls.projectsApp.url"
            >
                {{ $t("goToProjectList") }}
            </SmartLink>
            <button
                class="button hollow expanded"
                @click="closeOffPanel('copyProject')"
            >
                {{ $t("closePanel") }}
            </button>
        </template>

        <BaseForm
            v-else
            :errorText="$t('copyProjectError')"
            :model="model"
            :saveUrl="urls.projectsCopy"
            :successText="$t('copyProjectSuccess')"
            :vuelidate="$v.model"
            @cancel="closeOffPanel('copyProject')"
            @saved="onProjectCopied"
        >
            <FormField
                :schema="{
                    type: 'char',
                    label: $t('name'),
                    placeholder: $t('name'),
                }"
                v-model.trim="model.name"
                :vuelidate="$v.model.name"
            />

            <FormField
                :schema="{
                    type: 'toggle',
                    label: $t('shouldCopy.items'),
                }"
                v-model.trim="model.copy_params.items"
            />

            <FormField
                :schema="{
                    type: 'toggle',
                    label: $t('shouldCopy.owners'),
                }"
                v-model.trim="model.copy_params.owners"
            />

            <FormField
                :schema="{
                    type: 'toggle',
                    label: $t('shouldCopy.channels'),
                }"
                v-model.trim="model.copy_params.channels"
            />

            <FormField
                :schema="{
                    type: 'toggle',
                    label: $t('shouldCopy.targets'),
                }"
                v-model.trim="model.copy_params.targets"
            />

            <FormField
                :schema="{
                    type: 'toggle',
                    label: $t('shouldCopy.assets'),
                }"
                v-model.trim="model.copy_params.assets"
            />

            <FormField
                :schema="{
                    type: 'toggle',
                    label: $t('shouldCopy.metadata'),
                }"
                v-model.trim="model.copy_params.metadata"
            />
        </BaseForm>
    </div>
</OffPanel>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { required } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ProjectCopyOffpanel",
    mixins: [PilotMixin],
    data: () => ({
        model: {
            name: "",
            copy_params: {
                items: true,
                owners: true,
                channels: true,
                targets: true,
                assets: true,
                metadata: true,
            },
        },
        copyStarted: false,
    }),
    validations: {
        model: {
            name: { required },
        },
    },
    computed: {
        ...mapState("projelDetail", ["projel"]),
    },
    methods: {
        ...mapMutations("offPanel", ["closeOffPanel"]),
        onOpen() {
            this.model.name = this.$t("copyOf") + " " + this.projel.name
            this.model.id = this.projel.id
        },
        onProjectCopied() {
            this.copyStarted = true
        },
    },
    i18n: {
        messages: {
            fr: {
                copyOf: "Copie de",
                copyProject: "Copie de projet",
                copyProjectSuccess: "La copie a démarrée avec succès",
                copyProjectError: "Error lors du lancement de la copie",
                goToProjectList: "Aller à la liste des projets",
                shouldCopy: {
                    items: "Copier les contenus",
                    owners: "Copier les responsables",
                    channels: "Copier les canaux",
                    targets: "Copier les cibles",
                    assets: "Copier les fichiers",
                    metadata: "Copier les autres informations",
                },
            },
            en: {
                copyOf: "Copy of",
                copyProject: "Copy project",
                copyProjectSuccess: "The copy started successfully",
                copyProjectError: "Error when starting the copy",
                goToProjectList: "Go to the project list",
                shouldCopy: {
                    items: "Copy items",
                    owners: "Copy owners",
                    channels: "Copy channels",
                    targets: "Copy targets",
                    assets: "Copy assets",
                    metadata: "Copy other data",
                },
            },
        },
    },
}
</script>
