var util = require("util")
var events = require("events")

/**
 * Wait for the prosemirror menu to show up, than click on the nth menu element
 */
function clickPmMenu() {
    events.EventEmitter.call(this)
}

util.inherits(clickPmMenu, events.EventEmitter)

clickPmMenu.prototype.command = function (menuElementIndex) {
    this.api.waitForElementVisible(".ProseMirror-tooltip")
    this.api.elements(
        "css selector",
        ".ProseMirror-tooltip .ProseMirror-menuitem",
        (menuElements) => {
            this.api.elementIdClick(menuElements.value[menuElementIndex].ELEMENT, () => {
                this.emit("complete")
            })
        },
    )
    return this
}

module.exports = clickPmMenu
