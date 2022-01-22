/**
 * Wait for the element at `selector` to be visible, then click on it
 */
export function command(selector) {
    this.waitForElementVisible(selector).click(selector)

    return this
}
