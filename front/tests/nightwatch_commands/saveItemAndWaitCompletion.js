/**
 * Select some text in the `element`, starting at `start_pos` from the left border,
 * ending at `offset` from the start position.
 */
export function command() {
    this.waitForElementVisible(".ItemMiddleBarEdition .save.button")
        .assert.containsText(".ItemMiddleBarEdition .save.button", "Sauvegarder les modifications")
        .click(".ItemMiddleBarEdition .save.button")
        .waitForElementVisible(".ItemMiddleBarTabs")

    return this
}
