import { getFullUrl } from "../../main/src/tests/utils"

export let titleSelector = ".ItemContentFormField.title"
export let titleInputSelector = titleSelector + " .ItemContentFormField__widget"
export let pmSelector = ".ItemContentForm .ProseMirror"

export let lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"

export function _createItem(browser, itemTitle = "Epic title v1") {
    return browser
        .url(getFullUrl("/items/"))
        .click(".ToolBar__new a")
        .pause(500) // Wait for transition
        .click(".ItemAddPanel__ItemType:first-child a")
        .waitForElementVisible(titleInputSelector)
        .setValue(titleInputSelector, itemTitle)
        .click(".form__field__buttons button:first-child")
        .pause(300) // Wait for save
}
