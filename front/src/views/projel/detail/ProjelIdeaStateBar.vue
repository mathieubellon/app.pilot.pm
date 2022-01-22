<template>
<div
    v-if="isClosed || isIdea || isRejected"
    class="ProjelIdeaStateBar"
    :class="{ isClosed, isIdea, isRejected }"
>
    <span v-if="isClosed">{{ $t(isChannelRoute ? "channelClosed" : "projectClosed") }}</span>
    <span v-if="isIdea">
        {{ $t("projectIsSuggestion") }}
        <span v-if="!myPermissions.is_admin">({{ $t("adminNeeded") }})</span>
    </span>
    <span v-if="isRejected">{{ $t("projectIsRejected") }}</span>

    <!-- Start Action Buttons -->
    <div
        v-if="myPermissions.is_admin"
        class="ProjelIdeaStateBar__buttons"
    >
        <template v-if="isClosed">
            <button
                v-if="usageLimitReached('projects')"
                class="button is-small"
                disabled
            >
                {{ $t("maxProjectsReached") }}
            </button>
            <a
                v-else
                class="button is-small is-blue"
                @click="requestProjelStateUpdate('active')"
            >
                {{ $t("reopen") }}
            </a>
        </template>
        <template v-if="isIdea">
            <a
                class="button is-small is-blue"
                @click="requestProjelStateUpdate('active')"
            >
                {{ $t("acceptAndMakeActive") }}
            </a>
            <a
                class="button is-small is-red"
                @click="requestProjelStateUpdate('rejected')"
            >
                {{ $t("rejectSuggestion") }}
            </a>
        </template>
        <template v-if="isRejected">
            <a
                class="button is-small is-blue"
                @click="requestProjelStateUpdate('idea')"
            >
                {{ $t("reactiveSuggestion") }}
            </a>
        </template>
    </div>

    <!-- Confirm Modal -->
    <Modal
        name="updateProjelState"
        height="auto"
        width="800"
    >
        <div class="p-4">
            <h2 class="text-lg font-bold">
                {{ $t(isChannelRoute ? "theChannelWillBe" : "theProjectWillBe") }} {{ verb }}
            </h2>

            <div class="ProjelIdeaStateBar__confirm mt-2">
                <!-- Comment box -->
                <div
                    v-if="!isClosed"
                    class="ProjelIdeaStateBar__PreConfiguredNotif"
                >
                    <label>
                        <input
                            v-model="notifyAuthor"
                            class="mr-4"
                            type="checkbox"
                        />
                        {{ $t("authorWillBeNotified") }} ({{ authorEmail }}).
                        {{ $t("uncheckBox") }}
                    </label>
                </div>

                <div class="ProjelIdeaStateBar__PreConfiguredCommentBox">
                    <span class="text-small italic">{{ $t("preConfiguredCommentBox") }}</span>
                    <CommentBox
                        v-model="comment"
                        class="mt-4"
                        :contentType="contentTypes.Project"
                        :inactiveMentionGroups="inactiveMentionGroups"
                    />
                </div>

                <!-- Confirm Action Buttons -->
                <div class="ProjelIdeaStateBar__confirmButtons">
                    <SmartButtonSpinner
                        class="button is-blue mr-2"
                        name="confirmProjelStateUpdate"
                        @click.prevent="onConfirmClick"
                    >
                        {{ $t("confirm") }}
                    </SmartButtonSpinner>

                    <a
                        class="button"
                        @click="$modal.hide('updateProjelState')"
                    >
                        {{ $t("cancel") }}
                    </a>
                </div>
            </div>
        </div>
    </Modal>
</div>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import CommentBox from "@components/CommentBox.vue"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ProjelIdeaStateBar",
    mixins: [PilotMixin],
    components: {
        CommentBox,
    },
    data: () => ({
        notifyAuthor: true,
        comment: null,
        verb: "",
        // If a state change is requested, hold the name of the state (active/closed/idea/rejected)
        projelStateUpdateRequested: null,
    }),
    computed: {
        ...mapState("projelDetail", ["projel"]),
        ...mapGetters("projelDetail", [
            "isChannelRoute",
            "isProjectRoute",
            "inactiveMentionGroups",
        ]),
        ...mapGetters("usageLimits", ["usageLimitReached"]),
        ...mapGetters("users", ["myPermissions"]),
        isClosed() {
            return this.projel.state == "closed"
        },
        isIdea() {
            return this.projel.state == "idea"
        },
        isRejected() {
            return this.projel.state == "rejected"
        },
        authorEmail() {
            return this.projel.created_by_external_email
                ? this.projel.created_by_external_email
                : this.projel.created_by.email
        },
    },
    methods: {
        ...mapActions("projelDetail", ["confirmProjelStateUpdate"]),
        requestProjelStateUpdate(projelState) {
            this.projelStateUpdateRequested = projelState

            if (projelState == "active" && this.projel.state == "closed")
                this.verb = this.$t("reopened")
            else if (projelState == "active" && this.projel.state == "idea")
                this.verb = this.$t("validated")
            else if (projelState == "rejected" && this.projel.state == "idea")
                this.verb = this.$t("rejected")
            else if (projelState == "idea" && this.projel.state == "rejected")
                this.verb = this.$t("reactivated")

            let owners =
                this.projel.owners.map((owner) => "@" + owner.username).join(" ") || this.$t("none")
            let channelsList = this.projel.channels || []
            let channels =
                channelsList
                    .map((channel) => {
                        let channelOwners =
                                channel.owners.map((owner) => "@" + owner.username).join(" ") ||
                                this.$t("none"),
                            channelName = channel.name
                        return this.$t("channelListElement", { channelName, channelOwners })
                    })
                    .join("<br />") || this.$t("none")

            let stateUpdateMessage = this.isChannelRoute
                ? "channelStateUpdateMessage"
                : "projectStateUpdateMessage"
            this.comment = this.$t(stateUpdateMessage, {
                projelName: this.projel.name,
                verb: this.verb,
                projelUrl: window.location.origin + this.projel.url,
                owners,
                channels,
            })

            this.$modal.show("updateProjelState")
        },
        onConfirmClick() {
            this.confirmProjelStateUpdate({
                projelStateUpdateRequested: this.projelStateUpdateRequested,
                notifyAuthor: this.notifyAuthor,
                comment: this.comment,
            }).then(() => {
                this.$modal.hide("updateProjelState")
                this.projelStateUpdateRequested = null
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                adminNeeded: "seul un.e admin peut la valider/refuser",
                acceptAndMakeActive: "Accepter la proposition et rendre le projet actif",
                authorWillBeNotified: "L'auteur de la proposition sera alerté par email",
                channelClosed: "Ce canal est fermé",
                channelListElement: "{channelName} (responsables : {channelOwners})",
                channelStateUpdateMessage: `<p>Bonjour,<br />
Le canal "{projelName}" vient d'être {verb} ( <a href="{projelUrl}">{projelUrl}</a> ).</p>
<p>Responsable(s) : {owners}</p>`,
                confirm: "Je confirme",
                none: "Aucun",
                maxProjectsReached: "Impossible de réouvrir : maximum atteint",
                projectClosed: "Ce projet est fermé",
                projectIsRejected: "Cette proposition a été rejetée",
                projectIsSuggestion: "Ce projet est une proposition",
                reactivated: "ré-activé",
                reactiveSuggestion: "Ré-activer cette proposition",
                rejected: "rejeté",
                rejectSuggestion: "Refuser la proposition",
                reopen: "Réouvrir",
                reopened: "réouvert",
                projectStateUpdateMessage: `<p>Bonjour,<br />
Le projet "{projelName}" vient d'être {verb} ( <a href="{projelUrl}">{projelUrl}</a> ).</p>
<p>Responsable(s) : {owners}</p>
<p>Canaux :<br />
{channels}</p>`,
                theChannelWillBe: "Le canal sera ",
                theProjectWillBe: "Le projet sera ",
                uncheckBox: "Décochez la case si vous ne souhaitez pas l'avertir",
                preConfiguredCommentBox:
                    "Nous vous avons préparé un commentaire ci-dessous pour avertir les personnes liées au projet. Vous pouvez éditer librement ce commentaire.",
                validated: "validé",
                whenYouWillConfirm: "Quand vous cliquerez sur 'confirmer' : ",
            },
            en: {
                adminNeeded: "only one administrator can validate / reject it",
                acceptAndMakeActive: "Accept the proposal and make the project active",
                authorWillBeNotified: "The author of the proposal will be alerted by email",
                channelClosed: "This channel is closed",
                channelListElement: "{channelName} (owners : {channelOwners})",
                channelStateUpdateMessage: `<p>Hello,
The channel "{projelName}" has been {verb} (  <a href="{projelUrl}">{projelUrl}</a> ).</p>
<p>Owner(s) : {owners}</p>>`,
                confirm: "I confirm",
                maxProjectsReached: "Cannot reopen :: maximum reached",
                none: "None",
                projectClosed: "This project is closed",
                projectIsRejected: "This suggestion was rejected",
                projectIsSuggestion: "This project is a suggestion",
                reactivated: "reactivated",
                reactiveSuggestion: "Re-activate this proposal",
                rejected: "rejected",
                rejectSuggestion: "Refuse the proposal",
                reopen: "Reopen",
                reopened: "reopened",
                projectStateUpdateMessage: `<p>Hello,
The project "{projelName}" has been {verb} (  <a href="{projelUrl}">{projelUrl}</a> ).</p>

<p>Owner(s) : {owners}</p>

<p>Channels :<br />
{channels}</p>`,
                theChannelWillBe: "The channel will be ",
                theProjectWillBe: "The project will be ",
                uncheckBox: "Décochez la case si vous ne souhaitez pas l'avertir",
                preConfiguredCommentBox:
                    "We have prepared a comment below to warn people related to the project. You can edit this comment freely.",
                validated: "validated",
                whenYouWillConfirm: "When you click on 'confirm' : ",
            },
        },
    },
}
</script>

<style lang="scss">
.ProjelIdeaStateBar {
    @apply flex flex-grow justify-between items-center px-8 py-2;
}
.ProjelIdeaStateBar.isClosed {
    @apply bg-yellow-200 text-yellow-800;
}
.ProjelIdeaStateBar.isIdea {
    @apply bg-yellow-200;
}
.ProjelIdeaStateBar.isRejected {
    @apply bg-gray-200 text-gray-800;
}

.ProjelIdeaStateBar__confirm {
    flex-grow: 10;
    display: flex;
    flex-flow: column;
}
.ProjelIdeaStateBar__confirmButtons {
    display: flex;
    align-items: center;
    justify-content: right;
}
.ProjelIdeaStateBar__PreConfiguredCommentBox {
    background-color: #fafafa;
    padding: 1em;
    margin-bottom: 1em;
    border-radius: 5px;
    textarea {
        box-shadow: inset 0px -13px 15px 0px #ddd;
    }
}
.ProjelIdeaStateBar__PreConfiguredNotif {
    background-color: #fafafa;
    padding: 1em;
    margin-bottom: 1em;
    label {
        font-size: 1.1em;
        display: flex;
        justify-content: space-between;
    }
}
</style>
