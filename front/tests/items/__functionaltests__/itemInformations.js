import { setupNightwatchTest, getFullUrl } from "../../../main/src/tests/utils"
import { titleInputSelector, _createItem } from "../testUtils"

export function before(browser) {
    // Use a fixture to init batch of targets/channels/projects/users
    setupNightwatchTest(browser, "items.informations")
}

/**
 * Test the item informations panel
 */
export function guidelines(browser) {
    browser
        .url(getFullUrl("/items/1/"))
        .waitForElementVisible(titleInputSelector)
        .click("#tab-informations-link")
        .waitForElementVisible("#tab-informations")
        .click(".DrawerInformations__seeGuidelines")
        .waitForElementPresent(".offpanel-container")
        .pause(300) // Wait for the transition to end

        .assert.containsText(".offpanel-container", "Quoi et qui :\nItem guidelines")
        .assert.containsText(".offpanel-container", "Où :\nItem where")
        .assert.containsText(".offpanel-container", "Objectif :\nItem goal")
        .assert.containsText(".offpanel-container", "Contacts :\nItem contacts")
        .assert.containsText(".offpanel-container", "Sources :\nItem sources")
        .assert.containsText(".offpanel-container", "Portée :\nRégionale")
        .assert.containsText(".offpanel-container", "Photos disponibles : oui")
        .assert.containsText(".offpanel-container", "Faut-il envoyer un(e) photographe ? : oui")
        .assert.containsText(".offpanel-container", "Recherches nécessaires : oui")
        .assert.containsText(".offpanel-container", "Recherches documentaires nécessaires : oui")
        .assert.containsText(".offpanel-container", "Soutien rédactionnel nécessaire : oui")

        .click(".offpanel-header__close")
        .pause(500) // Wait for the transition to end
}

export function linkProject(browser) {
    browser.assert
        .containsText(".DrawerInformations__element.project", "Sélectionner un projet")
        .click(".DrawerInformations__element.project .DrawerInformations__pick")
        .waitForElementPresent(".ProjectPicker")
        .pause(300) // Wait for the transition to end

        // The 5 project fixtures are present
        .assert.elementsCount(".ProjectPicker .ProjectPickerElement", 5)

        // We can select one, and the offpanel immediatly close
        .click(".ProjectPicker .ProjectPickerElement:last-child")
        .waitForElementNotPresent(".ProjectPicker")
        .assert.containsText(".DrawerInformations__element.project", "Project5-active")

        // We can see the project description
        .click(".DrawerInformations__element.project .ItemDescription__toggleDescription")
        .waitForElementVisible(".DrawerInformations__element.project .ItemDescription__description")
        .assert.containsText(
            ".DrawerInformations__element.project .ItemDescription__description",
            "Project lorem ipsum dolor sit amet",
        )

        // We can unpick the project
        .click(".DrawerInformations__element.project .DrawerInformations__unpick")
        .waitForElementVisible(".DrawerInformations__element.project .DrawerInformations__pick")
}

export function linkChannel(browser) {
    browser.assert
        .containsText(".DrawerInformations__element.channel", "Sélectionner un canal")
        .click(".DrawerInformations__element.channel .DrawerInformations__pick")
        .waitForElementPresent(".ChannelPicker")
        .pause(300) // Wait for the transition to end

        // The 5 project fixtures are present
        .assert.elementsCount(".ChannelPicker .ChannelPickerElement", 5)

        // We can select one, and the offpanel immediatly close
        .click(".ChannelPicker .ChannelPickerElement:last-child")
        .waitForElementNotPresent(".ChannelPicker")
        .assert.containsText(".DrawerInformations__element.channel", "Channél5")

        // We can see the project description
        .click(".DrawerInformations__element.channel .ItemDescription__toggleDescription")
        .waitForElementVisible(".DrawerInformations__element.channel .ItemDescription__description")
        .assert.containsText(
            ".DrawerInformations__element.channel .ItemDescription__description",
            "Channel lorem îpsum dolor sit amet",
        )

        // We can unpick the project
        .click(".DrawerInformations__element.channel .DrawerInformations__unpick")
        .waitForElementVisible(".DrawerInformations__element.channel .DrawerInformations__pick")
}

export function linkTargets(browser) {
    browser.assert
        .containsText(".DrawerInformations__element.targets", "Ajouter ou retirer les cibles")
        .click(".DrawerInformations__element.targets .DrawerInformations__pick")
        .waitForElementPresent(".TargetPicker")
        .pause(300) // Wait for the transition to end

        // The 5 project fixtures are present
        .assert.elementsCount(".TargetPicker .TargetPickerElement", 5)

        // Select a first target
        .click(".TargetPicker .TargetPickerElement:last-child")
        .pause(500) // Wait for saving, we can't click on another PickerElement during loading
        // Select anoter target
        .click(".TargetPicker .TargetPickerElement:nth-child(4)")
        // Close the offpanel
        .click(".offpanel-header__close")
        .pause(500) // Wait for the transition to end
        .waitForElementNotPresent(".TargetPicker")
        .assert.containsText(".DrawerInformations__element.targets", "Cibles\nTarget3\nTarget5")

        // We can unpick the project
        .click(".DrawerInformations__element.targets .DrawerInformations__pick")
        .pause(300) // Wait for the transition to end
        .click(".TargetPicker .TargetPickerElement:nth-child(4)")
        .click(".offpanel-header__close")
        .pause(500) // Wait for the transition to end
        .waitForElementNotPresent(".TargetPicker")
        .assert.containsText(".DrawerInformations__element.targets", "Cibles\nTarget5")
}

export function linkOwners(browser) {
    browser.assert
        .containsText(".DrawerInformations__element.owners", "Ajouter / retirer des responsables")
        .click(".DrawerInformations__element.owners .DrawerInformations__pick")
        .waitForElementPresent(".UserPicker")
        .pause(300) // Wait for the transition to end

        // The 5 project fixtures are present + the test user = 6
        .assert.elementsCount(".UserPicker .UserPickerElement", 6)

        // Select a first target
        .click(".UserPicker .UserPickerElement:last-child")
        .pause(500) // Wait for saving, we can't click on another PickerElement during loading
        // Select anoter target
        .click(".UserPicker .UserPickerElement:nth-child(4)")
        // Close the offpanel
        .click(".offpanel-header__close")
        .pause(500) // Wait for the transition to end
        .waitForElementNotPresent(".UserPicker")
        .assert.containsText(".DrawerInformations__element.owners", "Responsables\n@John3\n@John6")

        // We can unpick the project
        .click(".DrawerInformations__element.owners .DrawerInformations__pick")
        .pause(300) // Wait for the transition to end
        .click(".UserPicker .UserPickerElement:nth-child(4)")
        .click(".offpanel-header__close")
        .pause(500) // Wait for the transition to end
        .waitForElementNotPresent(".UserPicker")
        .assert.containsText(".DrawerInformations__element.owners", "Responsables\n@John6")
}

export function after(browser) {
    browser.end()
}
