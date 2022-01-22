import { setupNightwatchTest, getFullUrl } from "../../../main/src/tests/utils"
import { titleInputSelector } from "../testUtils"

let charInputSelector = ".ItemContentFormField.char .ItemContentFormField__widget"
let twitterInputSelector = ".ItemContentFormField.twitter .ItemContentFormField__widget"
let integerInputSelector = ".ItemContentFormField.integer .ItemContentFormField__widget"

function assertInvalidField(browser, fieldSelector, errors, assert_invalid_button = true) {
    if (assert_invalid_button) {
        browser
            .waitForElementVisible(".ItemMiddleBarEdition .invalid")
            .assert.containsText(".ItemMiddleBarEdition .invalid", "Données invalides")
    }
    browser.assert.attributeContains(fieldSelector, "class", "has-error")
    for (let error of errors) {
        browser.assert.containsText(fieldSelector + " .ValidationErrors", error)
    }
}

export function before(browser) {
    setupNightwatchTest(browser, "items.content_validation")
}

/**
 * Test that the item content is validated
 */
export function itemContentValidation(browser) {
    let oversizedTweet = new Array(282).join("é")

    browser
        .url(getFullUrl("/items/1/"))
        .waitForElementVisible(charInputSelector)

        /**********
         * Validation for a required field
         **********/

        // Delete the 3 initial characters
        // Don't use .clearValue(charInputSelector) because this does not send actual keystrokes
        // and won't trigger item validation
        .click(charInputSelector)
        .keys([browser.Keys.BACK_SPACE, browser.Keys.BACK_SPACE, browser.Keys.BACK_SPACE])
    assertInvalidField(browser, ".ItemContentFormField.char", ["Ce champ est obligatoire"])

    // Go back to a valid state with a the cancel operation
    browser
        .click(".ItemMiddleBarEdition .cancel.button")

        /**********
         * Validation for twitter maxlength
         **********/

        .click(twitterInputSelector)
        .keys(oversizedTweet)
    assertInvalidField(browser, ".ItemContentFormField.twitter", [
        "Contenu trop long. Twitter autorise seulement 280 signes",
    ])
    // Go back to a valid state with a the cancel operation
    browser
        .click(".ItemMiddleBarEdition .cancel.button")

        /**********
         * Validation for min/max on integer
         **********/

        .click(integerInputSelector)
        .keys("6")
    assertInvalidField(browser, ".ItemContentFormField.integer", ["Valeur trop élevée (max 5)"])
    browser.click(integerInputSelector).keys([browser.Keys.BACK_SPACE, "0"])
    assertInvalidField(browser, ".ItemContentFormField.integer", ["Valeur trop faible (min 1)"])
    // Go back to a valid state with a the cancel operation
    browser.click(".ItemMiddleBarEdition .cancel.button")

    /**********
     * Server-side validation
     **********/

    // We would a need a way to mock the server response as error to go forward with this test
    /*
    # Make a client-side valid update
        char_input.send_keys('def')

        validation_error = HttpResponseBadRequest(json.dumps({
            'content': {
                'char': ['Epic server-side validation error',
                         'Monstruous server-side validation error']
            }
        }))
        # Simulate a server-side validation error
        with mock.patch('pilot.core.items.api.api.ItemRetrieveUpdate.dispatch',
                        return_value=validation_error):
            save_button = self.assert_and_get_save_button()
            save_button.click()

            # Wait for the request to complete
            time.sleep(1)

        self.assert_invalid_field(char_field,
                                  ['Epic server-side validation error',
                                   'Monstruous server-side validation error'],
                                  assert_invalid_button=False)
     */
}

/**
 * Test that we can see an error when the edition fail server-side
 */
export function serverSideErrorOnItemEdition(browser) {
    // We would a need a way to mock the server response as error to go forward with this test
    return

    browser
        /**********
         * Unsuccesful edition
         **********/
        .setValue(titleInputSelector, " again")
        .saveItemAndWaitCompletion()

        // Wait for the request to complete, with error
        .waitForElementVisible(".ItemMiddleBarEdition .error.button")
    self.containsText(".ItemMiddleBarEdition .error.button", "Erreur, sauvegarde non effecuée")
}

export function after(browser) {
    browser.end()
}
