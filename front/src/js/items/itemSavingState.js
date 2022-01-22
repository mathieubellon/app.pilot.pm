import moment from "moment"
import { getRandomId } from "@js/utils"

const SAVING_RECOVERY_STATE = {
    reconnecting: "reconnecting",
    xhr: "xhr",
    resolved: "resolved",
    failed: "failed",
}

/**
 * Track item saving start time and recovery attempt
 */
class ItemSavingState {
    constructor() {
        this.id = getRandomId()
        this.startTime = moment()
        this.recoveryState = null
    }

    setRecoveryState(recoveryState) {
        this.recoveryState = recoveryState
    }

    get isReconnecting() {
        return this.recoveryState == SAVING_RECOVERY_STATE.reconnecting
    }

    get isXhr() {
        return this.recoveryState == SAVING_RECOVERY_STATE.xhr
    }

    get isResolved() {
        return this.recoveryState == SAVING_RECOVERY_STATE.resolved
    }

    get isFailed() {
        return this.recoveryState == SAVING_RECOVERY_STATE.failed
    }
}

export { SAVING_RECOVERY_STATE, ItemSavingState }
