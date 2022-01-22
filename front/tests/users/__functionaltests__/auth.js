import { setupNightwatchTest, getFullUrl } from "../../../main/src/tests/utils"

export function login(browser) {
    setupNightwatchTest(browser)
    browser.assert
        .urlEquals(getFullUrl("/dashboard")) // Correctly landed on the dashboard
        .click(".MainMenu_element:nth-child(4)") // The menu is loaded
        .pause(500)
        .assert.urlEquals(getFullUrl("/projects/active")) // Correctly navigate
        .end()
}
