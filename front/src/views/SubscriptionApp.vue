<template>
<MainLayout class="SubscriptionApp">
    <span slot="title">{{ $t("subscription") }} {{ subscription.organization.name }}</span>

    <div slot="middlebar">
        <div class="tabs">
            <a
                class="tab"
                :class="{ 'is-active': currentTab == 'subscription' }"
                @click="currentTab = 'subscription'"
            >
                {{ $t("subscription") }}
            </a>
            <a
                class="tab"
                :class="{ 'is-active': currentTab == 'billingInfos' }"
                @click="currentTab = 'billingInfos'"
            >
                {{ $t("billingInformations") }}
            </a>
            <a
                class="tab"
                :class="{ 'is-active': currentTab == 'bills' }"
                @click="currentTab = 'bills'"
            >
                {{ $t("bills") }}
            </a>
            <a
                class="tab"
                :class="{ 'is-active': currentTab == 'card' }"
                @click="currentTab = 'card'"
            >
                {{ $t("card") }}
            </a>
            <a
                class="tab"
                :class="{ 'is-active': currentTab == 'inactiveDesks' }"
                @click="currentTab = 'inactiveDesks'"
            >
                {{ $t("inactiveDesks") }}
            </a>
        </div>
    </div>

    <div
        class="SubscriptionApp__content"
        slot="content"
    >
        <Loadarium name="subscription">
            <div
                v-if="currentTab == 'subscription'"
                class="SubscriptionApp__subscription"
            >
                <div
                    v-for="deskSubscription in subscription.desks"
                    class="SubscriptionApp__currentSubscription simple-panel"
                >
                    <div class="SubscriptionApp__currentSubscription__title">
                        {{ $t("desk") }} {{ deskSubscription.desk.name }}
                    </div>

                    <div v-if="deskSubscription.is_terminated">
                        {{ $t("subscriptionTerminated") }}
                    </div>

                    <div>
                        <span
                            v-html="$t('youHaveThisPlan', { plan: deskSubscription.plan.name })"
                        />
                        <template v-if="deskSubscription.plan.price">
                            ( {{ deskSubscription.plan.price }} )
                        </template>
                        .
                        <template v-if="!subscription.organization.manual_billing">
                            {{ $t("youCan") }}
                            <a @click="openChangePlan(deskSubscription)">{{ $t("changePlan") }}</a>
                        </template>
                        <span v-if="deskSubscription.is_deactivable">
                            {{ $t("or") }}
                            <a
                                class="text-alert"
                                @click="openDeactivateDesk(deskSubscription)"
                            >
                                {{ $t("deactivateDesk") }}
                            </a>
                        </span>
                        <span v-if="deskSubscription.is_running">
                            {{ $t("or") }}
                            <a
                                class="text-alert"
                                @click="openTerminateSubscription(deskSubscription)"
                            >
                                {{ $t("terminateSubscription") }}
                            </a>
                        </span>

                        <template v-if="!deskSubscription.is_deactivable">
                            <div v-if="subscription.organization.manual_billing">
                                {{
                                    $t("yourManualBilling", {
                                        amount: deskSubscription.billed_amount_display,
                                    })
                                }}
                            </div>
                            <div v-else>
                                {{
                                    $t("yourNextDeskBilling", {
                                        amount: deskSubscription.billed_amount_display,
                                        nextBillingDate,
                                    })
                                }}
                            </div>
                        </template>

                        <div v-if="deskSubscription.trial_period_end">
                            {{
                                $t("yourTrialWillEnd", {
                                    end: dateFormat(deskSubscription.trial_period_end),
                                })
                            }}
                        </div>
                    </div>

                    <div
                        v-if="!deskSubscription.is_deactivable"
                        class="SubscriptionApp__currentSubscription__usersBilled"
                    >
                        {{
                            $tc("billedUsers", deskSubscription.billed_users_count, [
                                deskSubscription.billed_users_count,
                            ])
                        }}.&nbsp;
                        <a
                            class="text-alert"
                            @click="openUsersList(deskSubscription)"
                        >
                            {{ $t("seeUsersList") }}
                        </a>
                    </div>

                    <div class="SubscriptionApp__currentSubscription__usageLimits">
                        <strong>{{ $t("yourConsumption") }} :</strong>
                        <div v-for="usage_limit in deskSubscription.usage_limits">
                            <span>{{ usage_limit.label }}</span>
                            <span>{{ usage_limit.usage_display }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div
                v-if="currentTab == 'billingInfos'"
                class="SubscriptionApp__billingInfos"
            >
                <div class="SubscriptionApp__invoices simple-panel">
                    <BillingAddressForm
                        ref="BillingAddressForm"
                        :organization="subscription.organization"
                    />
                    <SmartButtonSpinner
                        name="updateBillingAddress"
                        :timeout="3000"
                        @click="updateBillingAddress"
                    >
                        {{ $t("save") }}
                    </SmartButtonSpinner>
                </div>
            </div>

            <div
                v-if="currentTab == 'bills'"
                class="SubscriptionApp__bills"
            >
                <div class="SubscriptionApp__invoices simple-panel">
                    <h3>{{ $t("billedAmount") }}</h3>
                    <span v-if="subscription.subcription_items.length == 0">N/A</span>
                    <table class="table stack tight">
                        <tbody>
                            <tr v-for="deskSubscription in subscription.desks">
                                <th>{{ deskSubscription.desk.name }}</th>
                                <th v-if="!subscription.organization.manual_billing">
                                    {{ deskSubscription.billed_users_count }}
                                    {{ $t("users") }}
                                </th>
                                <td>{{ deskSubscription.billed_amount_display }}</td>
                            </tr>
                        </tbody>
                    </table>

                    <div v-if="!subscription.organization.manual_billing">
                        {{
                            $t("yourNextGlobalBilling", {
                                amount: subscription.billed_amount_display,
                                nextBillingDate,
                            })
                        }}
                    </div>

                    <h3>{{ $t("invoices") }}</h3>
                    <span v-if="subscription.invoices == 'error'">=== Stripe error ===</span>
                    <span v-else-if="subscription.invoices.length == 0">
                        {{ $t("noInvoices") }}
                    </span>
                    <table
                        v-else
                        class="table stack tight"
                    >
                        <tbody>
                            <tr v-for="invoice in subscription.invoices">
                                <th>{{ invoice.number }}</th>
                                <td>{{ invoice.amount_display }}</td>
                                <td>{{ invoice.date | dateFormat }}</td>
                                <td>
                                    <a
                                        :href="invoice.hosted_invoice_url"
                                        target="_blank"
                                    >
                                        {{ $t("seeDetails") }}
                                    </a>
                                </td>
                                <td>
                                    <a :href="invoice.invoice_pdf">{{ $t("downloadAsPdf") }}</a>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div
                v-if="currentTab == 'card'"
                class="SubscriptionApp__card"
            >
                <div class="simple-panel">
                    <Loadarium name="changeCard">
                        <div v-if="subscription.is_customer && subscription.card">
                            <p>
                                {{ $t("currentCard") }} "{{ subscription.card.brand }} XXXX XXXX
                                XXXX {{ subscription.card.last4 }}".
                            </p>
                            <p>
                                {{ $t("youCan") }}
                                <a @click="collectChangedCustomerCard">{{ $t("changeCard") }}</a>
                            </p>
                        </div>
                        <div v-else>
                            {{ $t("noCardData") }}
                        </div>
                    </Loadarium>
                </div>
            </div>

            <div
                v-if="currentTab == 'inactiveDesks'"
                class="SubscriptionApp__inactiveDesks"
            >
                <div
                    v-for="inactiveDesk in subscription.inactive_desks"
                    class="simple-panel"
                >
                    <h2>{{ $t("desk") }} {{ inactiveDesk.name }}</h2>
                    <table class="table stack tight">
                        <tbody>
                            <tr v-for="usage_limit in inactiveDesk.usage_limits">
                                <th>{{ usage_limit.label }}</th>
                                <td>{{ usage_limit.current_usage_display }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </Loadarium>

        <OffPanel
            name="changePlan"
            position="right"
            width="90%"
        >
            <div slot="offPanelTitle">{{ $t("changePlan") }}</div>
            <div
                v-if="currentDeskSubscription"
                slot="offPanelBody"
            >
                <table class="table stack">
                    <thead>
                        <tr>
                            <th></th>
                            <th v-for="subscriptionPlan in subscriptionPlans">
                                {{ subscriptionPlan.name }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <th>{{ $t("price") }}</th>
                            <td v-for="subscriptionPlan in subscriptionPlans">
                                {{ subscriptionPlan.display_price }}
                            </td>
                        </tr>
                        <tr>
                            <th>{{ $t("maxUsers") }}</th>
                            <td v-for="subscriptionPlan in subscriptionPlans">
                                {{ formatPlanLimit(subscriptionPlan.max_users) }}
                            </td>
                        </tr>
                        <tr>
                            <th>{{ $t("maxProjects") }}</th>
                            <td v-for="subscriptionPlan in subscriptionPlans">
                                {{ formatPlanLimit(subscriptionPlan.max_projects) }}
                            </td>
                        </tr>
                        <tr>
                            <th>{{ $t("maxItems") }}</th>
                            <td v-for="subscriptionPlan in subscriptionPlans">
                                {{ formatPlanLimit(subscriptionPlan.max_items) }}
                            </td>
                        </tr>
                        <tr>
                            <th>{{ $t("maxAssetStorage") }}</th>
                            <td v-for="subscriptionPlan in subscriptionPlans">
                                {{ subscriptionPlan.max_assets_storage }} Go
                            </td>
                        </tr>
                        <tr>
                            <th>{{ $t("advancedFeatures") }}</th>
                            <td v-for="subscriptionPlan in subscriptionPlans">
                                {{ subscriptionPlan.advanced_features | yesno }}
                            </td>
                        </tr>

                        <tr>
                            <td></td>
                            <td v-for="subscriptionPlan in subscriptionPlans">
                                <span
                                    v-if="
                                        currentDeskSubscription.is_running &&
                                        subscriptionPlan.id == currentDeskSubscription.plan.id
                                    "
                                >
                                    {{ $t("yourCurrentPlan") }}
                                </span>
                                <SmartButtonSpinner
                                    v-else
                                    name="changeSubscription"
                                    :timeout="1500"
                                    @click="onPlanSelected(subscriptionPlan)"
                                >
                                    {{ $t("selectThisPlan") }}
                                </SmartButtonSpinner>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </OffPanel>

        <OffPanel
            name="confirmExistingCard"
            position="right"
        >
            <div slot="offPanelTitle">{{ $t("changePlan") }}</div>
            <div slot="offPanelBody">
                <p v-if="subscriptionPlanSelected">
                    {{
                        $t("firstSubscriptionSummary", {
                            name: subscriptionPlanSelected.name,
                            price: subscriptionPlanSelected.display_price,
                        })
                    }}
                </p>

                <p v-if="subscription.card">
                    {{ $t("confirmExistingCard", { last4: subscription.card.last4 }) }}
                </p>

                <SmartButtonSpinner
                    name="changeSubscription"
                    :timeout="1500"
                    @click="confirmExistingCard"
                >
                    {{ $t("changePlan") }}
                </SmartButtonSpinner>

                <a @click="closeOffPanel('confirmExistingCard')">
                    {{ $t("cancel") }}
                </a>
            </div>
        </OffPanel>

        <OffPanel
            name="confirmFirstSubscription"
            position="right"
        >
            <div slot="offPanelTitle">{{ $t("changePlan") }}</div>
            <div slot="offPanelBody">
                <div
                    v-if="subscriptionPlanSelected"
                    class="simple-panel"
                >
                    {{
                        $t("firstSubscriptionSummary", {
                            name: subscriptionPlanSelected.name,
                            price: subscriptionPlanSelected.display_price,
                        })
                    }}
                </div>

                <BillingAddressForm
                    ref="BillingAddressFormFirstSubscription"
                    :organization="subscription.organization"
                />

                <label>
                    <input
                        v-model="acceptCGV"
                        type="checkbox"
                    />
                    <span v-html="$t('acceptCGV')" />
                </label>
                <div
                    v-if="$v.acceptCGV.$error"
                    class="form__field__error"
                >
                    {{ $t("pleaseAcceptCGV") }}
                </div>

                <SmartButtonSpinner
                    name="changeSubscription"
                    :timeout="1500"
                    @click="confirmFirstSubscription"
                >
                    {{ $t("confirmFirstSubscription") }}
                </SmartButtonSpinner>
            </div>
        </OffPanel>

        <OffPanel
            name="deactivateDesk"
            position="right"
        >
            <div slot="offPanelTitle">{{ $t("deactivateDesk") }}</div>
            <div slot="offPanelBody">
                <SmartButtonSpinner
                    class="alert"
                    name="deactivateDesk"
                    :timeout="1500"
                    @click="deactivateDesk"
                >
                    {{ $t("deactivateDesk") }}
                </SmartButtonSpinner>
            </div>
        </OffPanel>

        <OffPanel
            name="terminateSubscription"
            position="right"
        >
            <div slot="offPanelTitle">{{ $t("terminateSubscription") }}</div>
            <div slot="offPanelBody">
                <SmartButtonSpinner
                    class="alert"
                    name="terminateSubscription"
                    :timeout="1500"
                    @click="terminateSubscription"
                >
                    {{ $t("terminateSubscription") }}
                </SmartButtonSpinner>
            </div>
        </OffPanel>

        <OffPanel
            name="usersList"
            position="right"
        >
            <div slot="offPanelTitle">{{ $t("usersList") }}</div>
            <div
                v-if="currentDeskSubscription"
                slot="offPanelBody"
            >
                <div class="SubscriptionApp__billedUsersDetails">
                    <div
                        v-for="user in currentDeskSubscription.billed_users"
                        class="SubscriptionApp__billedUsersDetails__user"
                    >
                        {{ user.username }} - {{ user.email }}
                    </div>
                </div>
            </div>
        </OffPanel>
    </div>
</MainLayout>
</template>

<script>
import { mapMutations } from "vuex"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import moment from "moment"
import { dateFormat } from "@js/filters"
import { required } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"
import BillingAddressForm from "@views/account/BillingAddressForm.vue"

export default {
    name: "SubscriptionApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
        BillingAddressForm,
    },
    data: () => ({
        currentTab: "subscription",
        subscription: {
            is_customer: false,
            organization: {},
            desks: [],
            subcription_items: [],
            invoices: [],
            card: {},
            current_period_end: null,
        },
        subscriptionPlans: [],
        currentDeskSubscription: null,
        subscriptionPlanSelected: null,
        acceptCGV: false,
        dateFormat: dateFormat,
    }),
    validations: {
        acceptCGV: { required },
    },
    computed: {
        nextBillingDate() {
            return dateFormat(moment(this.subscription.current_period_end).add(1, "day"))
        },
    },
    methods: {
        ...mapMutations("loading", ["resetLoading"]),
        openChangePlan(deskSubscription) {
            this.currentDeskSubscription = deskSubscription
            this.openOffPanel("changePlan")
        },
        openDeactivateDesk(deskSubscription) {
            this.currentDeskSubscription = deskSubscription
            this.openOffPanel("deactivateDesk")
        },
        openTerminateSubscription(deskSubscription) {
            this.currentDeskSubscription = deskSubscription
            this.openOffPanel("terminateSubscription")
        },
        openUsersList(deskSubscription) {
            this.currentDeskSubscription = deskSubscription
            this.openOffPanel("usersList")
        },
        formatPlanLimit(value) {
            if (value == -1) return this.$t("unlimited")
            else return value
        },
        onPlanSelected(subscriptionPlan) {
            this.subscriptionPlanSelected = subscriptionPlan
            if (this.subscription.is_customer) {
                this.openOffPanel("confirmExistingCard")
            } else {
                this.openOffPanel("confirmFirstSubscription")
            }
            this.closeOffPanel("changePlan")
        },
        confirmExistingCard() {
            this.changeSubscription(this.subscriptionPlanSelected)
        },
        confirmFirstSubscription() {
            let formValidation = this.$refs.BillingAddressFormFirstSubscription.$v
            formValidation.$touch()
            this.$v.$touch()
            if (formValidation.$invalid || this.$v.$invalid) {
                return
            }

            this.collectInitialCustomerCard(this.subscriptionPlanSelected)
        },
        collectInitialCustomerCard(subscriptionPlan) {
            this.collectCustomerCard({
                description: subscriptionPlan.name,
                tokenCallback: (token) => {
                    this.changeSubscription(subscriptionPlan, token.id)
                },
            })
        },
        collectChangedCustomerCard() {
            this.collectCustomerCard({
                description: this.$t("changeCardTitle"),
                label: this.$t("update"),
                tokenCallback: (token) => {
                    this.changeCard(token.id)
                },
            })
        },
        collectCustomerCard({ description, label, tokenCallback }) {
            this.stripeCheckout.open({
                locale: window.pilot.currentLocale,
                currency: "eur",
                name: "Pilot",
                description: description,
                label: label,
                email: this.$store.state.users.me.email,
                billingAddress: false,
                shippingAddress: false,

                /**
                 * Callback called by stripe when the checkout is complete and the token is ready
                 */
                token: tokenCallback,
            })
        },
        changeSubscription(subscriptionPlan, token_id = null) {
            $httpX({
                name: "changeSubscription",
                commit: this.$store.commit,
                url: urls.subscriptionChange,
                method: "POST",
                data: {
                    desk_id: this.currentDeskSubscription.desk.id,
                    plan_id: subscriptionPlan.id,
                    token_id: token_id,
                    organization: this.subscription.organization, // To set the billing address on new customers
                },
            }).then((response) => {
                this.subscription = response.data
                this.currentDeskSubscription = null
                this.subscriptionPlanSelected = null
                this.closeOffPanel("changePlan")
                this.closeOffPanel("confirmFirstSubscription")
                this.closeOffPanel("confirmExistingCard")
                this.resetLoading("changeSubscription")
            })
        },
        changeCard(token_id) {
            $httpX({
                name: "changeCard",
                commit: this.$store.commit,
                url: urls.subscriptionChangeCard,
                method: "POST",
                data: {
                    token_id: token_id,
                },
            }).then((response) => {
                this.subscription = response.data
                this.resetLoading("changeCard")
            })
        },
        deactivateDesk() {
            $httpX({
                name: "deactivateDesk",
                commit: this.$store.commit,
                url: urls.subscriptionDeactivateDesk,
                method: "POST",
                data: {
                    desk_id: this.currentDeskSubscription.desk.id,
                },
            }).then((response) => {
                this.subscription = response.data
                this.currentDeskSubscription = null
                this.closeOffPanel("deactivateDesk")
                this.resetLoading("deactivateDesk")
            })
        },
        terminateSubscription() {
            $httpX({
                name: "terminateSubscription",
                commit: this.$store.commit,
                url: urls.subscriptionTerminate,
                method: "POST",
                data: {
                    desk_id: this.currentDeskSubscription.desk.id,
                },
            }).then((response) => {
                this.subscription = response.data
                this.currentDeskSubscription = null
                this.closeOffPanel("terminateSubscription")
                this.resetLoading("terminateSubscription")
            })
        },
        updateBillingAddress() {
            let validation = this.$refs.BillingAddressForm.$v
            validation.$touch()
            if (validation.$invalid) {
                return
            }

            $httpX({
                name: "updateBillingAddress",
                commit: this.$store.commit,
                url: urls.subscriptionUpdateBillingAddress,
                method: "PUT",
                data: {
                    organization: this.subscription.organization, // To update the billing address
                },
            }).then((response) => {
                setTimeout(() => {
                    this.resetLoading("updateBillingAddress")
                }, 2000)
            })
        },
    },
    created() {
        $httpX({
            name: "subscription",
            commit: this.$store.commit,
            url: urls.subscription,
            method: "GET",
        }).then((response) => {
            this.subscription = response.data
        })

        $httpX({
            name: "plans",
            commit: this.$store.commit,
            url: urls.subscriptionPlans,
            method: "GET",
        }).then((response) => {
            this.subscriptionPlans = response.data
        })

        this.stripeCheckout = StripeCheckout.configure({
            key: window.pilot.djangoSettings.STRIPE_PUBLIC_KEY,
        })
    },
    i18n: {
        messages: {
            fr: {
                acceptCGV:
                    "J'accepte les <a href='https://www.pilot.pm/policies/cgv/' target='_blank'>Condition Générales de Vente</a>",
                addLabel: "Ajouter un label",
                advancedFeatures: "Fonctionnalités avancées",
                amount: "Montant",
                billedAmount: "Montant facturé",
                billedUsers:
                    "Vous êtes facturé pour {0} utilisateur | Vous êtes facturé pour {0} utilisateurs",
                billing: "Facturation",
                bills: "Factures",
                billingInformations: "Informations de facturation",
                card: "Carte",
                confirmFirstSubscription: "Confirmer l'abonnement et payer",
                confirmExistingCard:
                    "Nous allons utiliser la carte se terminant par {last4} pour les paiements",
                consumption: "Consommation",
                changeCard: "changer de carte",
                changeCardTitle: "Changement de carte",
                changePlan: "Changer de formule",
                currentCard: "Vous êtes actuellement débité sur la carte",
                deactivateDesk: "Désactiver ce desk",
                downloadAsPdf: "Télécharger le PDF",
                firstSubscriptionSummary: "Vous avez sélectionné l'abonnement {name} pour {price}",
                inactiveDesks: "Desks désactivés",
                invoices: "Factures",
                maxAssetStorage: "Stockage maximum",
                maxItems: "Contenus maximum",
                maxProjects: "Projets maximum",
                maxUsers: "Utilisateurs maximum",
                nextBill: "Prochaine échéance",
                noCardData: "Aucune information de carte à afficher",
                noInvoices: "Pas encore de facture",
                periodStart: "Début de la période",
                pleaseAcceptCGV: "Veuillez accepter les Condition Générales de Vente",
                price: "Price",
                seeDetails: "Voir le détail",
                seeUsersList: "Voir la liste",
                selectThisPlan: "Choisir cette formule",
                subscription: "Abonnement",
                subscriptionTerminated:
                    "L'abonnement a été arrêté. Ce compte sera désactivé à la fin de la période.",
                terminateSubscription: "Arrêter cet abonnement",
                unlimited: "Illimité",
                yourConsumption: "Votre consommation actuelle est la suivante",
                yourCurrentPlan: "Votre formule actuelle",
                youHaveThisPlan: "Cet espace de travail bénéficie du plan <strong>{plan}</strong>",
                yourManualBilling: "Vous êtes facturés anuellement de {amount}.",
                yourNextDeskBilling:
                    "Votre prochaine facturation pour ce desk sera de {amount} HT le {nextBillingDate}",
                yourNextGlobalBilling:
                    "Vous serez facturé d'un total de {amount} HT le {nextBillingDate}",
                yourTrialWillEnd: "Votre période d'essai prendra fin le {end}",
                youCan: "Vous pouvez",
            },
            en: {
                acceptCGV:
                    "I accept the <a href='https://www.pilot.pm/policies/cgv/' target='_blank'>Terms Of Sale</a>",
                addLabel: "Add a label",
                advancedFeatures: "Advanced features",
                amount: "Amount",
                billedAmount: "Billed amount",
                billedUsers: "Billed users",
                billing: "Billing",
                billingInformations: "Billing informations",
                confirmFirstSubscription: "Confirm subscription and checkout",
                consumption: "Consumption",
                changePlan: "Change plan",
                deactivateDesk: "Deactivate this desk",
                downloadAsPdf: "Download as PDF",
                inactiveDesks: "Inactives desks",
                invoices: "Invoices",
                maxAssetStorage: "Maximum storage",
                maxItems: "Maximum contents",
                maxProjects: "Maximum projects",
                maxUsers: "Maximum users",
                nextBill: "Next bill",
                noInvoices: "No invoices yet",
                periodStart: "Period start",
                pleaseAcceptCGV: "Please accept the Terms Of Sale",
                price: "Price",
                seeDetails: "See details",
                selectThisPlan: "Select this plan",
                subscription: "Subscription",
                subscriptionTerminated:
                    "Subscription has been terminated. This account will be closed at the end of the period.",
                terminateSubscription: "Terminate this subscription",
                unlimited: "Unlimited",
                yourCurrentPlan: "You can",
            },
        },
    },
}
</script>

<style lang="scss">
.SubscriptionApp__content {
    font-size: 1.2em;
}

.SubscriptionApp__currentSubscription__title {
    font-size: 1.3em;
    font-weight: 800;
}
.SubscriptionApp__currentSubscription__usersBilled {
    font-weight: 600;
    margin: 1em 0;
}
.SubscriptionApp__currentSubscription__usageLimits {
    margin: 1em 0;
}

.SubscriptionApp__billedUsersDetails {
}
.SubscriptionApp__billedUsersDetails__user {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 0.3em;
}
</style>
