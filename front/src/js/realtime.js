import Vue from "vue"

const WS_SCHEME = window.location.protocol == "https:" ? "wss" : "ws"
const REALTIME_SERVER_URL = WS_SCHEME + "://" + window.location.host + "/rt/"

// Client to server message types
const C2S_MESSAGES = {
    DELETE_ELASTIC_ELEMENT: "delete_elastic_element",
    REGISTER_ON_ITEM: "register_on_item",
    SHARED_ITEM_AUTH: "shared_item_auth",
    UPDATE_USER_ACTIVITY: "update_user_activity",
    UPDATE_ITEM_CONTENT: "update_item_content",
}
// Server to client message types
const S2C_MESSAGES = {
    BROADCAST_ASSET_CONVERSION_STATUS: "broadcast_asset_conversion_status",
    BROADCAST_ITEM: "broadcast_item",
    BROADCAST_ITEM_CHANGES: "broadcast_item_changes",
    BROADCAST_USERS_ON_ITEM: "broadcast_users_on_item",
    INVALID_CHANGES: "invalid_changes",
}

const STATES = {
    INITIAL: "initial",
    CONNECTING: "connecting",
    OPEN: "open",
    CLOSED: "closed",
}

class RealTime {
    /***********************
     * Low-level API
     ************************/

    constructor() {
        this.socket = null
        this.connectPromise = null
        this.state = STATES.INITIAL
        this.messageHandlers = {}
        this.lastErrorEvent = null

        this.S2C_MESSAGES = S2C_MESSAGES
        this.STATES = STATES
    }

    addMessageHandler(type, handler) {
        if (!this.messageHandlers[type]) {
            this.messageHandlers[type] = []
        }
        this.messageHandlers[type].push(handler)
    }

    removeAllMessageHandlers() {
        this.messageHandlers = {}
    }

    connect() {
        // Already connected, nothing to do
        if (this.socket) return

        this.state = STATES.CONNECTING

        this.connectPromise = new Promise((resolve, reject) => {
            this.lastErrorEvent = null
            let socket = (this.socket = new WebSocket(REALTIME_SERVER_URL))
            this.socket.onopen = () => {
                this.state = STATES.OPEN
                resolve()
            }
            this.socket.onerror = (errorEvent) => {
                // Apply only if this socket is still the current one
                if (this.socket == socket) {
                    this.lastErrorEvent = errorEvent
                }
            }
            this.socket.onclose = () => {
                // Apply only if this socket is still the current one
                if (this.socket == socket) {
                    this.state = STATES.CLOSED
                    reject()
                }
            }
        })

        // The socket object may be null if there has been an error during its creation
        // ( SecurityError on IE11 for example )
        if (this.socket) {
            this.socket.onmessage = (messageEvent) => this.onMessage(messageEvent)
        }
    }

    disconnect() {
        // Not connected, nothing to do
        if (!this.socket) {
            return
        }

        this.socket.close()
        this.socket = null
        this.state = STATES.CLOSED
        this.connectPromise = null
    }

    reconnect() {
        this.disconnect()
        this.connect()
    }

    onMessage(messageEvent) {
        this.callMessageHandlers(JSON.parse(messageEvent.data))
    }

    callMessageHandlers(messageData) {
        let type = messageData.type || ""
        for (let handler of this.messageHandlers[type] || []) {
            handler(messageData)
        }
    }

    /**
     * Send a message to the realtime server through a websocket.
     * The socket must have been previously connected with realtime.connect().
     * Won't send anything if the socket has not been connected, or has been closed.
     */
    send(message) {
        // Either the socket has never been connected.
        // Or the socket is closed : we tried to connect but could not.
        // We don't try to connect anew, and can't send the message.
        if (this.state == STATES.CLOSED || this.state == STATES.INITIAL) {
            return
        }

        this.connectPromise.then(() => {
            this.socket.send(JSON.stringify(message))
        })
    }

    /***********************
     * Sendable messages
     ************************/

    sharedItemAuth(token) {
        this.send({
            type: C2S_MESSAGES.SHARED_ITEM_AUTH,
            token: token,
        })
    }

    registerOnItem(itemId) {
        this.send({
            type: C2S_MESSAGES.REGISTER_ON_ITEM,
            item_id: itemId,
        })
    }

    updateUserActivity(userActivity) {
        this.send({
            type: C2S_MESSAGES.UPDATE_USER_ACTIVITY,
            user: userActivity,
        })
    }

    updateItemContent(changes, selection) {
        this.send({
            type: C2S_MESSAGES.UPDATE_ITEM_CONTENT,
            changes: changes,
            selection: selection,
        })
    }

    deleteElasticElement(fieldName, index) {
        this.send({
            type: C2S_MESSAGES.DELETE_ELASTIC_ELEMENT,
            field_name: fieldName,
            index: index,
        })
    }
}

export default Vue.observable(new RealTime())
