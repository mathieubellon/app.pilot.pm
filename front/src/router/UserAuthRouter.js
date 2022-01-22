import Login from "@views/users/auth/Login"
import Registration from "@views/users/auth/Registration"
import PasswordReset from "@views/users/auth/PasswordReset"
import PasswordResetConfirm from "@views/users/auth/PasswordResetConfirm"
import InvitationConfirm from "@views/users/auth/InvitationConfirm"

export default {
    mode: "history",
    routes: [
        {
            path: "/",
            name: "home",
            redirect: "/login/",
        },
        {
            path: "/login/",
            name: "login",
            component: Login,
        },
        {
            path: "/registration/",
            name: "registration",
            component: Registration,
        },
        {
            path: "/password/reset/:email?",
            name: "passwordReset",
            component: PasswordReset,
        },
        {
            path: "/password/reset/confirm/:uidb64/:token/",
            name: "passwordResetConfirm",
            component: PasswordResetConfirm,
        },
        {
            path: "/users/confirm/:token/",
            name: "invitationConfirm",
            component: InvitationConfirm,
        },
    ],
}
