import { setupNightwatchTest, getFullUrl } from "../../../main/src/tests/utils"
import { titleInputSelector, _createItem } from "../testUtils"

/**
 * Test the item comments panel
 */
export function itemComments(browser) {
    let atwhoXpath = "//div[contains(@style,'display: block') and contains(@class, 'atwho-view')]"

    setupNightwatchTest(browser)

    // Make a new item to test comments
    _createItem(browser)

    browser
        .url(getFullUrl("/items/1/"))
        .waitForElementVisible(titleInputSelector)

        // Open the comment tab
        .click("#tab-comments-link")
        .waitForElementVisible("#tab-comments")
        .pause(200) // Wait for the transition to end

        // Send a first comment
        .setValue("#tab-comments textarea", "This is an awesome comment")
        .click("#tab-comments button")
        .waitForElementVisible(".commentsListElement")

        .assert.elementsCount(".commentsList .commentsListElement", 1)
        .assert.containsText(".commentsListElement:first-child", "This is an awesome comment") // Our comment
        .assert.containsText(".commentsListElement:first-child", "John1") // Our username

        // Check the autocompletion on @mentions
        .setValue("#tab-comments textarea", "Please reply me @")
        .useXpath()
        .waitForElementVisible(atwhoXpath)
        .assert.containsText(atwhoXpath, "John1") // Our username

        .end()
}
