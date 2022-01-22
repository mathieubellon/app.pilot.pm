import { setupNightwatchTest, getFullUrl } from "../../../main/src/tests/utils"
import { titleInputSelector, _createItem } from "../testUtils"

/**
 * Test the item versions panel
 */
export function itemVersions(browser) {
    setupNightwatchTest(browser)

    // Make a new item to test versions
    _createItem(browser)

    browser
        .url(getFullUrl("/items/1/"))
        .waitForElementVisible(titleInputSelector)

        // Create 2 new versions
        .clearValue(titleInputSelector)
        .setValue(titleInputSelector, "Epic title v2")
        .saveItemAndWaitCompletion()
        .clearValue(titleInputSelector)
        .setValue(titleInputSelector, "Epic title v3")
        .saveItemAndWaitCompletion()
        .click("#tab-versions-link")

        // They should appear in the version tab
        .waitForElementVisible("#tab-versions")
        .assert.elementsCount("#tab-versions .DrawerHistory__element", 3)

        // We can visualize a previous version
        .click("#tab-versions .DrawerHistory__element:nth-child(2)")
        .pause(50)
        .assert.containsText(".ItemContentFieldReadOnly__content.title", "Epic title v2")

        // We can see the differences between two versions
        .click("#tab-versions .DrawerHistory__element:nth-child(1)")
        .waitVisibleThenClick(
            "#tab-versions .DrawerHistory__element:nth-child(1) .DrawerHistory__showDiff",
        )
        .waitForElementVisible(".ItemContentFieldReadOnly__content.title del") // Wait for the diff to load
        .assert.containsHtml(
            ".ItemContentFieldReadOnly__content.title",
            "Epic title <del>v2</del><ins>v3</ins>",
        )

        // We can select with which version we want to diff
        .click(
            "#tab-versions .DrawerHistory__element:nth-child(3) .DrawerHistory__compareWithVersion a",
        )
        .pause(500) // Wait for the diff to load
        .assert.containsHtml(
            ".ItemContentFieldReadOnly__content.title",
            "Epic title <del>v1</del><ins>v3</ins>",
        )

        // We can restore an old version
        .click("#tab-versions .DrawerHistory__element:nth-child(3)")
        .waitVisibleThenClick(
            "#tab-versions .DrawerHistory__element:nth-child(3) .DrawerHistory__restore",
        )
        .waitVisibleThenClick(
            "#tab-versions .DrawerHistory__element:nth-child(3) .DrawerHistory__confirmRestoration",
        )
        .waitForElementVisible(titleInputSelector)

        // The title is updated after restoration
        .pause(500) // Wait for the content to load
        .assert.valueContains(titleInputSelector, "Epic title v1")

        // A new version is created after restoration
        .pause(500) // Wait for the versions to reload
        .click("#tab-versions-link")
        .waitForElementVisible("#tab-versions")
        .assert.elementsCount("#tab-versions .DrawerHistory__element", 4)

        // We can upgrade to a major version
        .waitVisibleThenClick(
            "#tab-versions .DrawerHistory__element:nth-child(1) .DrawerHistory__createMajorVersion",
        )
        .waitVisibleThenClick(
            "#tab-versions .DrawerHistory__element:nth-child(1) .DrawerHistory__confirmUpgradeMajorVersion",
        )
        .pause(2000) // Wait for the versions to reload. This operation is suprisingly slow.
        // No new version is created after createMajorVersion
        .assert.elementsCount("#tab-versions .DrawerHistory__element", 4)
        // The latest version is now v2.0 instead of v1.4
        .assert.containsText("#tab-versions .DrawerHistory__element:nth-child(1)", "Version 2.0")

        .end()
}
