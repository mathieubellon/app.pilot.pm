import { setupNightwatchTest, getFullUrl, pgPool } from "../../../main/src/tests/utils"

export function createProject(browser) {
    setupNightwatchTest(browser)
    browser
        .url(getFullUrl("/projects/"))
        .waitForElementVisible(".ToolBar__new button")
        .click(".ToolBar__new button")
        .setValue(".form__field__name input", "Epic project")
        .pause(100)
        .click(".form__field__buttons button:first-child")
        .pause(500)
        .queryDb("SELECT * FROM projects_project", (pgResponse, done) => {
            browser.assert.equal(pgResponse.rows.length, 1)
            let project = pgResponse.rows[0]
            browser.assert.equal(project.name, "Epic project")
            done()
        })
        .end()
}
