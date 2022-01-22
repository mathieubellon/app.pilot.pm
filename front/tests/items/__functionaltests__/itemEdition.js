import _ from "lodash"
import { setupNightwatchTest, getFullUrl } from "../../../main/src/tests/utils"
import {
    titleSelector,
    titleInputSelector,
    pmSelector,
    lorem_ipsum,
    _createItem,
} from "../testUtils"

export function before(browser) {
    setupNightwatchTest(browser)
}

/**
 * Test that we can create an item with a title
 */
export function createItem(browser) {
    _createItem(browser)

    browser
        .url(getFullUrl("/items/1/"))
        .waitForElementVisible(titleInputSelector)
        .assert.valueContains(titleInputSelector, "Epic title v1")
}

/**
 * Test that we can edit the item content
 */
export function itemEdition(browser) {
    browser
        .waitForElementVisible(titleInputSelector)
        // No save button at loading
        .assert.elementNotPresent(".ItemMiddleBarEdition .save.button")

        /**********
         * Succesful edition
         **********/
        .setValue(titleInputSelector, " edited")
        // Title has been modified, the save button should be active
        .saveItemAndWaitCompletion()
        // Check that the item has been edited
        .assert.itemContentEquals(1, "title", "Epic title v1 edited")

        /**********
         * Global cancel edition
         **********/
        .setValue(titleInputSelector, " again")
        // The input content has been updated
        .assert.valueContains(titleInputSelector, "Epic title v1 edited again")
        // Cancel the edition through the global control
        .click(".ItemMiddleBarEdition .cancel.button")
        // The input content has been reseted
        .assert.valueContains(titleInputSelector, "Epic title v1 edited")
        // Content has been reseted, the save button is disabled again
        .assert.elementNotPresent(".ItemMiddleBarEdition .save.button")

        /**********
         * Field-specific cancel edition
         **********/
        .setValue(titleInputSelector, " again")
        // The input content has been updated
        .assert.valueContains(titleInputSelector, "Epic title v1 edited again")
        // Cancel the edition through the field-specific control
        .click(titleSelector + " .ItemContentFormField__restoreContentField")
        // The input content has been reseted
        .assert.valueContains(titleInputSelector, "Epic title v1 edited")
        // Content has been reseted, the save button is disabled again
        .assert.elementNotPresent(".ItemMiddleBarEdition .save.button")
}

/**
 * Test that we can change the item status
 */
export function itemState(browser) {
    let stateSelector =
        ".ItemStateDropdown__menu .ItemStateDropdown__stateListPanel__state:nth-child(2)"

    browser
        .waitForElementVisible(".ItemMiddleBarTabs .ItemStateDropdown__toggle")
        .assert.containsText(".ItemMiddleBarTabs .ItemStateDropdown__toggle", "Brouillon")
        .click(".ItemStateDropdown__toggle")
        .waitForElementVisible(stateSelector, 2000) // The state are loaded asynchroneously, let them some time to load
        // Start state change process
        .click(stateSelector)
        // We can cancel
        .waitForElementVisible(".ItemStateDropdown__menu button.cancel")
        .click(".ItemStateDropdown__menu button.cancel")

        // Now let's validate
        .waitForElementVisible(stateSelector)
        .pause(500) // Wait for the transition to end
        .click(stateSelector)
        .waitForElementVisible(".ItemStateDropdown__menu button.save")
        .setValue(".ItemStateDropdown__menu textarea", "Awesome state changing")
        .pause(1000) // Wait for the transition to end
        .click(".ItemStateDropdown__menu button.save")

        // Check that the state is now active
        .waitForElementVisible(stateSelector)
        .pause(100)
        .assert.cssClassPresent(stateSelector, "active")

        // The state change has been saved
        .queryDb(
            "SELECT workflow_workflowstate.name " +
                "FROM items_item INNER JOIN workflow_workflowstate " +
                "ON items_item.workflow_state_id = workflow_workflowstate.id " +
                "WHERE items_item.id=1",
            (pgResponse, done) => {
                let response = pgResponse.rows[0]
                browser.assert.equal(response["name"], "validation_ready")
                done()
            },
        )

        // Check that the comment has been saved
        .click("#tab-comments-link")
        .waitForElementVisible("#tab-comments")
        .pause(200) // Wait for the transition to end
        .assert.elementsCount(".commentsList .commentsListElement", 1)
        .assert.containsText(".commentsListElement:first-child", "Awesome state changing") // Our comment
        .assert.containsText(".commentsListElement:first-child", "John1") // Our username

        // Close the state panel
        .click(pmSelector)
}

/**
 * Test that we can use the prosemirror editor to enter and modify some text
 */
export function prosemirrorWorks(browser) {
    browser
        // Type in some text
        .waitForElementVisible(pmSelector)
        .click(pmSelector)
        .keys(lorem_ipsum)
        .pause(100)
        .assert.containsText(".ItemContentForm .ProseMirror", lorem_ipsum)

        // Strong mark
        .selectPmText(pmSelector, 103, 37)
        // Expect that the tooltip menubar will appear
        .clickPmMenu(0)
        .pause(100)

        // Emphasis mark
        .click(pmSelector) // Reset click position
        .selectPmText(pmSelector, 170, 40)
        .clickPmMenu(1)
        .pause(100)

        // Save this new content
        .saveItemAndWaitCompletion()
        // Expect the doc to have the correct marks
        .assert.itemContentEquals(1, "body", {
            type: "doc",
            content: [
                {
                    type: "paragraph",
                    content: [
                        { text: "Lorem ipsum ", type: "text" },
                        { text: "dolor", type: "text", marks: [{ type: "strong" }] },
                        { text: " sit ", type: "text" },
                        { text: "amet", type: "text", marks: [{ type: "em" }] },
                        { text: ", consectetur adipiscing elit", type: "text" },
                    ],
                },
            ],
        })

        // Canceling with ctrl+Z
        .click(pmSelector)
        .keys([browser.Keys.CONTROL, "z"])
        .keys([browser.Keys.CONTROL])
        .saveItemAndWaitCompletion()
        .assert.itemContentEquals(1, "body", {
            type: "doc",
            content: [
                {
                    type: "paragraph",
                    content: [
                        { text: "Lorem ipsum ", type: "text" },
                        { text: "dolor", type: "text", marks: [{ type: "strong" }] },
                        { text: " sit amet, consectetur adipiscing elit", type: "text" },
                    ],
                },
            ],
        })
}

/**
 * Test that we can annotate some text in the prosemirror editor
 */
export function annotations(browser) {
    let annotation, annotationId, annotation2, annotationId2
    let newCommentSelector = ".ItemDetailTextAnnotations.editable .new-comment"
    let mainCommentSelector = ".ItemDetailTextAnnotations.editable .main-comment"
    let secondaryCommentSelector = ".ItemDetailTextAnnotations.editable .comment:nth-child(2)"
    let json_user = {
        id: 1,
        username: "John1",
    }

    browser
        // Reload the page to reset prosemirror history
        .url(getFullUrl("/items/1/"))
        .waitForElementVisible(pmSelector)

        /**********
         * Cancel annotation creation
         **********/
        .selectPmText(pmSelector, 103, 40)
        // Let's begin annotation creation
        .clickPmMenu(8)

        // Annotations should now be displayed
        .waitForElementPresent(newCommentSelector)
        .click(newCommentSelector + " .cancel")
        // Annotation must disappear
        .waitForElementNotPresent(newCommentSelector)

        /**********
         * Create an annotation
         **********/
        // Now let's do an actual annotation
        .pause(50)
        .selectPmText(pmSelector, 103, 40)
        .clickPmMenu(8)

        // Annotations should now be displayed
        .waitForElementPresent(newCommentSelector)
        // There should be an input waiting for us to comment
        .setValue(newCommentSelector + " textarea", "This is an awesome comment")
        // Save this new comment
        .click(newCommentSelector + " .save")
        // And now an auto-save of the new annotation should be triggered
        // Wait a little, and assert that the item has a new annotation
        .pause(500)
        .queryDb("SELECT annotations FROM items_item WHERE id=1", (pgResponse, done) => {
            let item = pgResponse.rows[0]
            let values = _.values(item.annotations)
            browser.assert.equal(values.length, 1)
            annotation = values[0]
            annotationId = annotation["id"]
            json_user.avatar = annotation["mainComment"]["user"]["avatar"]
            browser.assert.deepEqual(annotation["mainComment"]["user"], json_user)
            browser.assert.equal(annotation["mainComment"]["content"], "This is an awesome comment")
            browser.assert.deepEqual(annotation["comments"], [])
            browser.assert.deepEqual(annotation["range"], { from: 13, to: 18 })
            browser.assert.equal(annotation["resolved"], false)
            browser.assert.equal(annotation["resolvedBy"], null)
            browser.assert.equal(annotation["selectedText"], "dolor")
            done()
        })

        /**********
         * Create a comment
         **********/
        // Position the cursor on the annotation
        .moveToElement(pmSelector, 105, 5)
        .mouseButtonClick()
        // Make another comment on the same annotation
        .setValue(newCommentSelector + " textarea", "This is a second comment")
        .click(newCommentSelector + " .save")

        // And now an auto-save of the new annotation should be triggered
        // Wait a little, and assert that the item has a new annotation
        .pause(500)
        .queryDb("SELECT annotations FROM items_item WHERE id=1", (pgResponse, done) => {
            let item = pgResponse.rows[0]
            annotation = item.annotations[annotationId]
            browser.assert.equal(annotation["comments"].length, 1)
            let comment = annotation["comments"][0]
            browser.assert.deepEqual(comment["user"], json_user)
            browser.assert.equal(comment["content"], "This is a second comment")
            done()
        })

        /**********
         * Edit the main comment
         **********/
        .click(mainCommentSelector + " .edit")
        .setValue(mainCommentSelector + " textarea", " edited")
        .click(mainCommentSelector + " .save")

        // Wait for auto-save
        .pause(500)
        .queryDb("SELECT annotations FROM items_item WHERE id=1", (pgResponse, done) => {
            annotation = pgResponse.rows[0].annotations[annotationId]
            browser.assert.equal(
                annotation["mainComment"]["content"],
                "This is an awesome comment edited",
            )
            done()
        })

        /**********
         * Edit the secondary comment
         **********/
        .click(secondaryCommentSelector + " .edit")
        .setValue(secondaryCommentSelector + " textarea", " edited")
        .click(secondaryCommentSelector + " .save")

        // Wait for auto-save
        .pause(500)
        .queryDb("SELECT annotations FROM items_item WHERE id=1", (pgResponse, done) => {
            annotation = pgResponse.rows[0].annotations[annotationId]
            browser.assert.equal(
                annotation["comments"][0]["content"],
                "This is a second comment edited",
            )
            done()
        })

        /**********
         * Delete the secondary comment
         **********/
        .click(secondaryCommentSelector + " .delete")
        // Wait for auto-save
        .pause(500)
        .queryDb("SELECT annotations FROM items_item WHERE id=1", (pgResponse, done) => {
            annotation = pgResponse.rows[0].annotations[annotationId]
            browser.assert.equal(annotation["comments"].length, 0)
            done()
        })

        /**********
         * Create another annotation
         **********/
        .click(pmSelector) // Reset click position
        .selectPmText(pmSelector, 103, 40)
        // Begin annotation creation
        .clickPmMenu(8)
        .waitForElementPresent(newCommentSelector)
        // There should be an input waiting for us to comment
        .setValue(newCommentSelector + " textarea", "This is a double annotation !")
        // Save this new comment
        .click(newCommentSelector + " .save")
        // And now an auto-save of the new annotation should be triggered
        // Wait a little, and assert that the item has a new annotation
        .pause(500)
        .queryDb("SELECT annotations FROM items_item WHERE id=1", (pgResponse, done) => {
            let item = pgResponse.rows[0]
            let pairs = _.toPairs(item.annotations)
            browser.assert.equal(pairs.length, 2)
            annotationId2 = pairs[0][0] == annotationId ? pairs[1][0] : pairs[0][0]
            annotation2 = item.annotations[annotationId2]

            //  The text is correct
            browser.assert.equal(
                annotation2["mainComment"]["content"],
                "This is a double annotation !",
            )
            // The range is the same, this is ok
            browser.assert.deepEqual(annotation2["range"], { from: 13, to: 18 })
            done()
        })

        /**********
         * Annotation display
         **********/
        // Position the cursor on the annotation
        .moveToElement(pmSelector, 105, 5)
        .mouseButtonClick()
        .pause(200)
        .assert.elementsCount(".ItemDetailTextAnnotations.editable .AnnotationElement", 2)

        /**********
         * Annotation resolving
         **********/

        // We can resolve annotations, and they're still in the data but not displayed.
        // The annotations should be displayed by date of creation desc, so the first
        // to be displayed must be the latest we created (annotation2).
        .click(".ItemDetailTextAnnotations.editable .AnnotationElement:first-child .resolve input")
        .pause(50)
        .click(
            ".ItemDetailTextAnnotations.editable .AnnotationElement__confirmResolve a:first-child",
        )
        .pause(100)
        .queryDb("SELECT annotations FROM items_item WHERE id=1", (pgResponse, done) => {
            let item = pgResponse.rows[0]
            // There's still the 2 annotations in the data
            browser.assert.equal(_.toPairs(item.annotations).length, 2)
            annotation2 = item.annotations[annotationId2]
            browser.assert.equal(annotation2["resolved"], True)
            browser.assert.equal(annotation2["resolvedBy"], json_user)
            done()
        })
        // The resolved annotation is not displayed anymore
        .assert.elementsCount(".AnnotationElement", 1)
}

export function after(browser) {
    browser.end()
}
