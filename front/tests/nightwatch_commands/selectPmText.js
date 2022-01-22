/**
 * Select some text in the `element`, starting at `start_pos` from the left border,
 * ending at `offset` from the start position.
 */
export function command(selector, startPos, offset) {
    // that approach doesn't seems to work well
    // Fallback on selecting a word with a double click
    this.moveToElement(selector, startPos, 5)
        .pause(10)
        .mouseButtonDown(0)
        .pause(10)
        .moveToElement(selector, startPos + offset, 5)
        .pause(10)
        .mouseButtonUp(0)
}
