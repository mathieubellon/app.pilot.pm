<template>
<Modal
    :adaptive="true"
    height="95%"
    :max-height="800"
    :max-width="1000"
    :name="`sharings-${sharingTarget.type}`"
    :pivotY="0.3"
    width="100%"
    @closed="onModalClosed"
    @opened="onModalOpened"
>
    <div
        class="p-4 h-full overflow-y-auto"
        ref="modalContent"
    >
        <!-- We need an empty span when not loading, to push to the right the toggleActivitiesVisibility  -->
        <span class="absolute">
            <Loadarium name="fetchSharings" />
        </span>

        <a
            class="button is-small float-right relative z-10"
            @click="$modal.hide(`sharings-${sharingTarget.type}`)"
        >
            {{ $t("close") }}
        </a>

        <div class="mb-2 relative">
            <div class="form__field__label">
                {{ $t("email") }}
            </div>

            <ValidationErrors :validation="$v.sharingModel.email" />

            <div
                class="InputStyling flex flex-wrap items-center p-0"
                :class="{
                    'is-invalid': $v.sharingModel.email.$error,
                }"
            >
                <div
                    v-for="(recipient, index) in recipients"
                    class="flex items-center justify-between content-center border border-gray-300 rounded py-1 px-3 mx-1 mt-1 mb-1"
                    :key="index"
                >
                    <span>
                        {{ recipient }}
                    </span>

                    <a @click="removeRecipient(index)">
                        <Icon
                            class="text-gray-500 w-5 h5 -mt-0.5"
                            name="Close"
                        />
                    </a>
                </div>

                <input
                    class="flex-grow border-transparent w-56"
                    :class="{
                        'is-invalid': $v.sharingModel.email.$error,
                    }"
                    ref="emailInput"
                    placeholder="john@doe.com"
                    type="text"
                    v-model.trim="sharingModel.email"
                    @blur="onEmailInputBlur"
                    @focus="onEmailInputFocus"
                    @input="onEmailInput"
                    @keydown.enter="addRecipientFromInput"
                />
            </div>

            <transition
                enter-active-class="animated fadeIn"
                leave-active-class="animated fadeOut"
            >
                <div
                    v-show="emailInputFocused"
                    class="absolute bg-white w-full border border-gray-300 z-10"
                >
                    <h3 class="font-bold p-2">{{ $t("recentlyUsed") }}</h3>

                    <!--
                    Here it's important to use @mousedown instead of @click,
                    so it gets handled before the @blur from the emailInput
                     -->
                    <div
                        v-for="email in filteredEmailHistory"
                        class="p-2 w-full cursor-pointer hover:bg-gray-200"
                        @mousedown="addRecipient(email)"
                    >
                        {{ email }}
                    </div>
                    <span
                        v-if="!filteredEmailHistory.length"
                        class="p-2"
                    >
                        {{ $t("noMatch") }}
                    </span>
                </div>
            </transition>
        </div>

        <div v-if="isCreateSharingsVisible">
            <FormField
                :schema="{
                    type: 'char',
                    label: $t('passwordLabel'),
                    placeholder: $t('password'),
                }"
                v-model.trim="sharingModel.password"
                :vuelidate="$v.sharingModel.password"
            />

            <FormField
                :schema="{
                    type: 'text',
                    label: $t('message'),
                    placeholder: $t('messagePlaceholder'),
                }"
                v-model.trim="sharingModel.message"
                :vuelidate="$v.sharingModel.message"
            />

            <FormField
                v-model="sharingModel.is_editable"
                :schema="{
                    type: 'toggle',
                    label: this.$t('isEditable'),
                }"
            />

            <div
                v-if="cannotCreateWithoutRecipients"
                class="form__field__error"
            >
                {{ $t("cannotCreateWithoutRecipients") }}
            </div>

            <ButtonSpinner
                class="button is-blue"
                :isLoading="isCreatingSharings"
                @click="createSharingsWithRecipients()"
            >
                {{ $t("send") }}
            </ButtonSpinner>

            <button
                class="button ml-2"
                @click="recipients = []"
            >
                {{ $t("cancel") }}
            </button>
        </div>

        <div v-else>
            <SharingsModalElement
                v-for="sharing in sharingsWithRecipient"
                :key="sharing.token"
                :sharing="sharing"
            />

            <div
                v-if="sharingsWithRecipient.length == 0"
                class="alert-panel is-yellow"
            >
                {{ $t("noDirectSharingYet") }}
            </div>

            <hr class="my-4" />

            <template v-if="sharingLink">
                <h2 class="font-bold">{{ $t("sharingLink") }}</h2>

                <input
                    class="SharingElement__link cursor-pointer"
                    readonly
                    type="text"
                    :value="sharingLink.public_url"
                />

                <Deletarium
                    :confirmDeleteButtonText="$t('confirmDeactivate')"
                    :confirmDeletionMessage="$t('thisActionCannotBeUndone')"
                    :loadingName="`deactivateSharing-${sharingLink.token}`"
                    @delete="deactivateSharing(sharingLink)"
                >
                    <template
                        slot="notRequested"
                        slot-scope="{ requestDeletion }"
                    >
                        <button
                            class="button is-red mt-4"
                            @click="requestDeletion()"
                        >
                            {{ $t("deactivateSharingLink") }}
                        </button>
                    </template>
                </Deletarium>
            </template>

            <template v-else>
                <SmartButtonSpinner
                    class="button is-blue"
                    name="createSharing"
                    :timeout="2000"
                    @click="createSharingLink()"
                >
                    {{ $t("createSharingLink") }}
                </SmartButtonSpinner>
            </template>
        </div>

        <div class="help-text">
            <div class="help-text-title">
                <Icon
                    class="help-text-icon"
                    name="Share"
                />
                <span>{{ $t("contentsSharing") }}</span>
            </div>
            <div
                v-html="$t('explainSharings')"
                class="help-text-content"
            />
        </div>
    </div>
</Modal>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { email } from "vuelidate/lib/validators"
import Fuse from "fuse.js/dist/fuse.common.js"
import { LocalStorageWrapper } from "@js/localStorage.js"
import { parseQueryString } from "@js/queryString"
import PilotMixin from "@components/PilotMixin"
import ButtonSpinner from "@components/ButtonSpinner"
import SharingsModalElement from "./SharingsModalElement"

const EMPTY_SHARING = {
    email: "",
    password: "",
    message: "",
    is_editable: true,
}

let localHistory = new LocalStorageWrapper("SharingsModal.history")

export default {
    name: "SharingsModal",
    mixins: [PilotMixin],
    components: {
        ButtonSpinner,
        SharingsModalElement,
    },
    props: {
        sharingTarget: Object,
    },
    data: () => ({
        sharingModel: {},
        recipients: [],
        emailFuse: null,
        emailInputFocused: null,
        recipientsHistory: [],
        isCreatingSharings: false,
        cannotCreateWithoutRecipients: false,
    }),
    validations: {
        sharingModel: {
            email: { email },
        },
    },
    computed: {
        ...mapState("sharings", ["sharings"]),
        isCreateSharingsVisible() {
            return this.recipients.length > 0
        },
        sortedSharings() {
            return _.reverse(_.sortBy(this.sharings, (sharing) => sharing.created_at))
        },
        sharingsWithRecipient() {
            return this.sortedSharings.filter((s) => s.email)
        },
        sharingLink() {
            return _.find(this.sortedSharings, (s) => !s.email)
        },
        filteredEmailHistory() {
            let emails
            let query = this.sharingModel.email
            if (!query) {
                emails = this.recipientsHistory
            } else {
                emails = this.emailFuse.search(query).map((r) => r.item)
            }

            return emails.filter((email) => !this.recipients.includes(email))
        },
    },
    methods: {
        ...mapActions("sharings", ["fetchSharings", "createSharing", "deactivateSharing"]),
        addRecipient(email) {
            this.sharingModel.email = ""
            this.$v.sharingModel.email.$reset()
            this.emailInputFocused = false

            // Don't add an email twice
            if (this.recipients.includes(email)) {
                return
            }

            this.recipients.push(email)

            // If it exists, remove this email from the history
            _.pull(this.recipientsHistory, email)
            // Put the latest email at the top of the history
            this.recipientsHistory.unshift(email)
            // Save the history to the window.localStorage
            localHistory.set(this.recipientsHistory)
        },
        addRecipientFromInput() {
            let email = this.sharingModel.email
            if (email) {
                // We don't want the email validator to show up right away when the user start typing.
                // Wait for the user to hit enter or blur away from the input to validate the email.
                this.$v.sharingModel.email.$touch()
                if (!this.$v.sharingModel.email.$invalid) {
                    this.addRecipient(email)
                }
            }
        },
        removeRecipient(index) {
            this.recipients.splice(index, 1)
        },
        onEmailInput() {
            // We don't want the email validator to show up right away when the user start typing.
            // Apply the validation only when the blur has already $touched the validation.
            if (this.$v.sharingModel.email.$error) {
                this.$v.sharingModel.email.$touch()
            }
        },
        onEmailInputFocus() {
            this.emailInputFocused = true
        },
        onEmailInputBlur(event) {
            this.emailInputFocused = false
            this.addRecipientFromInput()
        },
        createSharingsWithRecipients() {
            this.cannotCreateWithoutRecipients = false
            if (this.recipients.length == 0) {
                this.cannotCreateWithoutRecipients = true
                return
            }

            this.isCreatingSharings = true

            let promises = []
            for (let email of this.recipients) {
                let sharing = _.defaults({}, { email }, this.sharingModel)
                promises.push(this.createSharing(sharing))
            }

            Promise.all(promises).then(() => {
                this.isCreatingSharings = false
                this.recipients = []
                this.sharingModel = _.assign({}, EMPTY_SHARING, this.sharingTarget)
            })
        },
        createSharingLink() {
            this.createSharing(this.sharingTarget)
        },
        onModalOpened() {
            this.sharingModel = _.assign({}, EMPTY_SHARING, this.sharingTarget)

            // Each sharing display its shared links into a read-only input.
            // When the user click on that input, select all its content for an easy copy-paste
            $(this.$refs.modalContent).on("click", ".SharingElement__link", function () {
                $(this).select()
            })

            // Reload the sharings in the background, in case there has been some updates
            this.fetchSharings(this.sharingTarget)
        },
        onModalClosed() {
            $(this.$refs.modalContent).off("click")
        },
    },
    watch: {
        recipientsHistory() {
            this.emailFuse.setCollection(this.recipientsHistory)
        },
    },
    created() {
        // Emails in local history
        let savedHistory = localHistory.get()
        if (savedHistory) {
            this.recipientsHistory = savedHistory
        }

        // Search into those emails
        this.emailFuse = new Fuse(this.recipientsHistory, {
            findAllMatches: true,
            threshold: 0.1,
        })
    },
    mounted() {
        // Modal auto-open ( from a notification )
        let queryParams = parseQueryString(document.location.search)
        let showSharingsModal = (queryParams.showSharingsModal || [])[0]
        if (showSharingsModal) {
            this.$modal.show("sharings")
        }
    },
    i18n: {
        messages: {
            fr: {
                cannotCreateWithoutRecipients: "Merci de renseigner au moins un email destinataire",
                contentsSharing: "Partages de contenus",
                confirmDeactivate: "Ok, désactiver",
                createSharingLink: "Créer un lien de partage ( accès en lecture seule )",
                deactivateSharingLink: "Désactiver le lien de partage",
                explainSharings:
                    "Le partage permet d'envoyer des contenus à un contact externe au logiciel, " +
                    "pour relecture ou collaboration sur l'édition.<br />" +
                    "Vous pouvez aussi créer un lien de partage à diffuser, " +
                    "qui permet un accès en lecture seule",

                isEditable: "Permettre au contact de modifier le contenu",
                messagePlaceholder: "Message...",
                noDirectSharingYet: "Pas encore de partage direct",
                noMatch: "Pas de résultat",
                passwordLabel: "Protéger le contenu par mot de passe (optionnel)",
                recentlyUsed: "Utilisés récemment",
                recipients: "Destinataires",
            },
            en: {
                cannotCreateWithoutRecipients: "Please fill at least one recipient email",
                contentsSharing: "Contents sharing",
                confirmDeactivate: "Ok, deactivate",
                createSharingLink: "Create a sharing link ( read-only access )",
                deactivateSharingLink: "Deactivate the sharing link",
                explainSharings:
                    "You can share contents with a contact outside the software, " +
                    "for validation or collaboration on the edition.<br />" +
                    "You can also create sharing link to distribute, " +
                    "which enable a read-only access",
                isEditable: "Allow recipient to edit the content",
                messagePlaceholder: "Message...",
                noDirectSharingYet: "No direct sharing yet",
                noMatch: "No match",
                passwordLabel: "Protect content with password (optionnal)",
                recentlyUsed: "Recently used",
                recipients: "Recipients",
            },
        },
    },
}
</script>
