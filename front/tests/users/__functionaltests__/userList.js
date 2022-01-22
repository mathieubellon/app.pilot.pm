import { setupNightwatchTest, getFullUrl, testServerOutput } from "../../../main/src/tests/utils"

export function userList(browser) {
    setupNightwatchTest(browser, "users.user_list")
    browser
        .url(getFullUrl("/users/"))
        .pause(1000)
        .assert.elementsCount(".userlist .usercontainer", 10)
        .click("#app-body .tabs .tabs__title:last-child")
        .pause(1000)
        .assert.elementsCount(".userlist .usercontainer", 5)
        .end()
}

export function userInvitation(browser) {
    setupNightwatchTest(browser)

    let email = "rick.astley@meh.com"
    testServerOutput.startCapture()

    browser
        .url(getFullUrl("/users/"))
        .pause(1000)
        .click(".userlist__callout button") // Open the invite form
        .pause(".invitation-form__field") // Wait for the invite form to be displayed
        .setValue(".invitation-form__field:first-child input", email) // set email
        .click(".invitation-form__field__radio__input:first-child") // set group
        .click(".invitation-form__field:last-child .button") // submit
        .pause(1000)
        .click("#app-body .tabs .tabs-title:nth-child(2)") // Go to the invited users tab
        .pause(1000)
        .assert.elementsCount(".userlist .usercontainer", 1)
        .assert.containsText(".user-list__element__infos__contact", email)
        .perform(() => {
            testServerOutput.stopCapture()
            let out = testServerOutput.getCapturedOutput()
            browser.assert.ok(out.includes("To: " + email))
            browser.assert.ok(
                out.includes(
                    "Merci de cliquer sur le lien ci-dessous pour confirmer votre email et terminer votre inscription",
                ),
            )
        })
        .end()
}
