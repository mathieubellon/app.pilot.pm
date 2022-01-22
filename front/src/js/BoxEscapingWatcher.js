import _ from "lodash"
import $ from "jquery"
import { keyCodes } from "@js/utils"

let activeWatchers = []

function handleDocumentClick(event) {
    // Ignore if the click target is not inside the DOM anymore.
    // This may happen when a v-if triggers and remove the target from the DOM ( ex: Loadarium )
    // IE11 does not understands document.contains, we need to use document.body.contains
    if (!document.body.contains(event.target)) {
        return
    }

    for (let watcher of activeWatchers) {
        watcher.handleDocumentClick(event)
    }
}

function handleKeydown(event) {
    let key = event.which || event.keyCode
    if (key == keyCodes.ESCAPE) {
        for (let watcher of activeWatchers) {
            watcher.handleEscapeKey(event)
        }
    }
}

/***
 * This class helps handle the use case
 * "A box opens somewhere on the screen and should disappears when the user click outside the box or hit the ESC key".
 * This apply mainly to some kind of dropdown or modal.
 *
 * The opener of such a box can create a BoxEscapingWatcher to be notified when it should close the box.
 * It takes two params :
 * - A function that returns a list of dom elements that are considered "inside the box"
 * - A callback to call when the use wish to escape ( make disappears ) the box
 *
 * The document event listeners are optimized to run only when there's at least one watcher active.
 *
 * Simplest usage example :
 *
 * let escapingWatcher = new BoxEscapingWatcher(
 *     () => document.querySelector("#myBox"),
 *     () => { closeMyBox(); escapingWatcher.stopWatching() }
 * )
 * escapingWatcher.startWatching()
 */
export default class BoxEscapingWatcher {
    constructor(getDomElements, onEscape) {
        this.getDomElements = getDomElements
        this.onEscape = onEscape
        this.watching = false
    }

    handleDocumentClick(event) {
        let clickOutside = true
        for (let domElement of this.getDomElements()) {
            if (!domElement) {
                continue
            }
            if (domElement.contains(event.target)) {
                clickOutside = false
            }
        }

        if (clickOutside) {
            this.onEscape(event)
        }
    }

    handleEscapeKey(event) {
        this.onEscape(event)
    }

    startWatching() {
        if (this.watching) {
            return
        }

        this.watching = true
        activeWatchers.push(this)

        if (activeWatchers.length == 1) {
            $(document).on("mousedown", handleDocumentClick)
            $(document).on("keydown", handleKeydown)
        }
    }

    stopWatching() {
        if (!this.watching) {
            return
        }

        this.watching = false
        _.remove(activeWatchers, this)

        if (activeWatchers.length == 0) {
            $(document).off("mousedown", handleDocumentClick)
            $(document).off("keydown", handleKeydown)
        }
    }
}
