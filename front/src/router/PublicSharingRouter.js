import NotFoundComponent from "@components/NotFoundComponent"

import Sharing from "@views/sharings/public/Sharing"
import SharingHeader from "@views/sharings/public/SharingHeader"
import SharedItem from "@views/sharings/public/SharedItem"
import SharedItemHeader from "@views/sharings/public/SharedItemHeader"

export default {
    mode: "history",
    routes: [
        {
            path: "/sharings/:token",
            name: "sharing",
            components: {
                header: SharingHeader,
                body: Sharing,
            },
        },

        {
            path: "/sharings/:token/items/:itemId",
            name: "sharedItem",
            components: {
                header: SharedItemHeader,
                body: SharedItem,
            },
        },

        { path: "*", component: NotFoundComponent },
    ],
}
