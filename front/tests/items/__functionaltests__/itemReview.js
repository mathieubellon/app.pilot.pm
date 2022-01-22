import { setupNightwatchTest, getFullUrl } from "../../../main/src/tests/utils"
import { titleInputSelector, pmSelector, lorem_ipsum } from "../testUtils"

function _openReviewTab(browser) {
    browser.click("#tab-reviews-link").waitForElementVisible("#tab-reviews").pause(500) // Wait for the transition to end
}

function _createItemSharing(browser, email, password, message, isEditable) {
    browser
        .click(".DrawerSharings__createItemSharing") // Start review creation
        .waitForElementPresent(".offpanel-container")
        // Make a read-only, password-less review
        .setValue(".CreateReview__email", email)
        .setValue(".CreateReview__password", password)
        .setValue(".CreateReview__message", message)
    if (!isEditable)
        // We need a  pause here, otherwise the checkbox click isn't registered
        browser.pause(100).click(".CreateReview__isEditable")
    browser
        .click(".offpanel-container button:first-child")
        .waitForElementNotPresent(".offpanel-container", 2000) // The validation have a slow animation, wait 2s
}

function _goToLastReviewUrl(browser) {
    let reviewUrl
    browser
        .getAttribute(
            ".DrawerSharings__review:first-child .DrawerSharings__review__url a",
            "href",
            (result) => (reviewUrl = result.value),
        )
        .perform((client, done) => {
            client.url(reviewUrl, () => done())
        })
}

export function before(browser) {
    // Use a fixture to init an item
    setupNightwatchTest(browser, "items.review")
}

let itemUrl = getFullUrl("/items/1/")
let reviewSelector = ".DrawerSharings__review:first-child"

/**
 * Test the item review panel
 */
export function itemReviewCreation(browser) {
    browser.url(itemUrl).waitForElementVisible(pmSelector)

    /**********
     * Review creation
     **********/
    _openReviewTab(browser)
    _createItemSharing(browser, "chuck@norris.com", "", "A message for Chuck", false)

    browser.assert // Move the mouse on the detail selector so the details are open
        .elementsCount(".DrawerSharings .DrawerSharings__review", 1)
        .assert.containsText(reviewSelector, "chuck@norris.com")
        .assert.containsText(reviewSelector, "En attente")

    /**********
     * Check Content
     **********/
    _goToLastReviewUrl(browser)
    // The message should appear
    browser
        .waitForElementPresent(".ItemPublicSharedItemHeader__title")
        .click(".ItemPublicSharedItemHeader__title")
        .waitForElementPresent(".offpanel-container")
        .pause(300) // Wait for the transition to end
        .assert.containsText(".offpanel-container", "john.doe1@example.com")
        .assert.containsText(".offpanel-container", "A message for Chuck")
        .assert.containsText(".offpanel-container", "Version : 1.0")
        .assert.containsText(".offpanel-container", "Canal : Review Channel")
        .assert.containsText(".offpanel-container", "Projet : Review Project")
        .click(".offpanel-header__close")
        .pause(500) // Wait for the transition to end
        .assert.containsText(".ItemContentFieldReadOnly__content.title", "Review title")
        .assert.containsText(".ItemContentFieldReadOnly__content.body", lorem_ipsum)
}

export function itemReviewRejection(browser) {
    /**********
     * Reject Review
     **********/

    browser
        .click(".PublicFormItemApp__form__buttons a")
        .waitForElementPresent("textarea")
        .setValue("textarea", "Chuck say NO")
        .click("a.reject")

        /**********
         * Review is not accessible after response
         **********/

        .refresh()
        .waitForElementVisible(".ItemPublicSharingApp__fullscreen.expired")
        .assert.containsText("body", "Ce lien de partage n'est plus valable.")

        /**********
         * Review is rejected on the review list
         **********/

        .url(itemUrl)
        .waitForElementVisible(pmSelector)
    _openReviewTab(browser)
    browser
        .click(".DrawerSharings__review__comment a")
        .assert.containsText(".DrawerSharings__review__commentText", "Chuck say NO")
        .assert.cssClassPresent(reviewSelector, "rejected")
        .assert.containsText(reviewSelector, "Document non validé")
}

export function itemReviewApproval(browser) {
    /**********
     * Approve Review
     **********/

    // Make an editable, password-protected review
    _createItemSharing(browser, "chuck@norris.com", "password", "A message for Chuck", true)
    browser.assert.elementsCount(".DrawerSharings .DrawerSharings__review", 2)

    /**********
     * Password protection
     **********/

    _goToLastReviewUrl(browser)
    browser
        .waitForElementVisible(".simple-panel")
        .assert.containsText(".simple-panel", "Cette page est protégée par un mot de passe")
        .setValue("#id_password", "password")
        .click("button")

        /**********
         * Modify review content, then approve
         **********/

        .waitForElementVisible(titleInputSelector)
        .setValue(titleInputSelector, " edited")
        .click(pmSelector)
        // Replace "dolor" by "gollum"
        .selectPmText(pmSelector, 100, 35)
        .keys([browser.Keys.BACK_SPACE, "gollum"])
        // Replace "amet" by "ergo"
        .selectPmText(pmSelector, 172, 35)
        .keys([browser.Keys.BACK_SPACE, "ergo"])
        // Replace "elit" by "gloria"
        .selectPmText(pmSelector, 375, 35)
        .keys([browser.Keys.BACK_SPACE, "gloria"])
        .click(".ItemPublicSharedItemHeader__button.save")
        .pause(100)
        .click(".PublicFormItemApp__form__buttons a")
        .waitForElementPresent("textarea")
        .setValue("textarea", "Chuck say YES")
        .click("a.approve")
}

export function itemReviewMerging(browser) {
    browser
        .url(itemUrl)
        .waitForElementVisible(pmSelector)

        /**********
         * Make a conflicting change, after the review
         **********/

        .url(itemUrl)
        .waitForElementVisible(pmSelector)

        .click(pmSelector)
        // Replace "dolor" by "invictus"
        .selectPmText(pmSelector, 103, 37)
        .keys([browser.Keys.BACK_SPACE, "invictus"])
        .saveItemAndWaitCompletion()

        // (V1.0 = initial version, V1.1= version created for the conflict)
        .assert.containsText("#tab-versions-link", "Version 1.1")

    /**********
     * See review edited content
     **********/

    _openReviewTab(browser)

    browser
        .click(".DrawerSharings__review__comment a")
        .assert.containsText(".DrawerSharings__review__commentText", "Chuck say YES")

        .moveToElement(".DrawerSharings__review__seeReview", 0, 0) // Get out of the comment, and wait for transition
        .pause(800)
        .click(".DrawerSharings__review__seeReview")
        .waitForElementVisible(".ItemContentFieldReadOnly__content.title")
        .assert.containsText(".ItemContentFieldReadOnly__content.title", "Review title edited")
        .assert.containsText(
            ".ItemContentFieldReadOnly__content.body",
            "Lorem ipsum gollum sit ergo, consectetur adipiscing gloria",
        )
        .assert.containsText(
            ".ItemMiddleBarReview",
            "Vous consultez la copie envoyée à chuck@norris.com",
        )

        /**********
         * See diff with content at the time of the review
         **********/

        .click(".DrawerSharings__review__seeChangesToVersionSent")
        .assert.containsHtml(
            ".ItemContentFieldReadOnly__content.body",
            'Lorem ipsum <del class="diff-deleted domerge ProseMirror-widget" contenteditable="false">dolor </del>' +
                '<span class="diff-inserted domerge">gollum </span>sit ' +
                '<del class="diff-deleted domerge ProseMirror-widget" contenteditable="false">amet, </del>' +
                '<span class="diff-inserted domerge">ergo, </span>consectetur adipiscing ' +
                '<del class="diff-deleted domerge ProseMirror-widget" contenteditable="false">elit</del>' +
                '<span class="diff-inserted domerge">gloria</span>',
        )

        /**********
         * See diff with current content
         **********/

        .click(".DrawerSharings__seeModifications")
        // The version with invictus take precedence, and is unperformable
        .assert.containsText(".ItemContentFieldReadOnly__content.body", "Lorem ipsum invictus sit")
        // The other change is performable, so it should display
        .assert.containsHtml(
            ".ItemContentFieldReadOnly__content.body",
            'class="diff-deleted domerge">amet, </span><ins class="diff-inserted domerge ProseMirror-widget"',
        )
        .assert.elementsCount(".ItemDetailReviewChanges .ItemDetailReviewChanges__reviewChange", 1)
        .assert.containsText(".ItemDetailReviewChanges__reviewChange", "chuck@norris.com")
        .assert.containsText(".ItemDetailReviewChanges__reviewChange", "A ajouté :\ngollum")
        .assert.containsText(".ItemDetailReviewChanges__reviewChange", "A supprimé :\ndolor")
        .assert.containsText(".ItemDetailReviewChanges__reviewChange", "Nouveau texte :\ninvictus")

        /**********
         * Merge with current content
         **********/

        // Refuse the change from  amet to ergo
        .click(".ItemContentFieldReadOnly__content.body ins.ProseMirror-widget")
        .click(".popper button.alert")

        // Now do the merge
        .click("a.DrawerSharings__mergeReview")
        .waitForElementVisible(titleInputSelector)
        // Change has been applied on the title
        .assert.valueContains(titleInputSelector, "Review title edited")
        // Conflicting change has not been applied
        // Rejected change has not been applied
        // Accepted change has been applied
        .assert.containsText(
            pmSelector,
            "Lorem ipsum invictus sit amet, consectetur adipiscing gloria",
        )

        // A new version 1.2 has been created (v1.0 = initial version, v1.1= version created for the conflict)
        .assert.containsText("#tab-versions-link", "Version 1.2")

        // Version has the right comment
        .click("#tab-versions-link")
        .waitForElementVisible("#tab-versions")
        .assert.containsText(
            "#tab-versions",
            "Version créée à partir des modifications de chuck@norris.com",
        )
}

export function after(browser) {
    browser.end()
}
