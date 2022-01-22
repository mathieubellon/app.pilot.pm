import _ from "lodash"
const DiffMatchPatch = require("diff-match-patch")
import $monitoring from "@js/monitoring"

const DIFF_TIMEOUT = 5
const wordDelimiters = /[ \n\t]/

/**
 * The main Differ object, with our custom timeout
 */
let diffMatchPatch = new DiffMatchPatch()
diffMatchPatch.Diff_Timeout = DIFF_TIMEOUT

/**
 * Split a text into an array of strings.  Reduce the texts to a string
 * of hashes where each Unicode character represents one word.
 * Modifies wordArray and wordHash parameters.
 */
function diff_wordsToCharsMunge(text, wordArray, wordHash) {
    let chars = []
    let wordEnd = -1

    // Walk the text, pulling out a substring for each line.
    // text.split('\n') would would temporarily double our memory footprint.
    // Modifying text would create many large strings to garbage collect.
    while (text && text.length > 0) {
        let match = text.search(wordDelimiters)
        wordEnd = match > -1 ? match : text.length - 1
        let word = text.substring(0, wordEnd + 1)
        text = text.substring(wordEnd + 1)

        if (word in wordHash) {
            chars.push(String.fromCharCode(wordHash[word]))
        } else {
            wordArray.push(word)
            wordHash[word] = wordArray.length - 1
            chars.push(String.fromCharCode(wordArray.length - 1))
        }
    }
    return chars.join("")
}

function textDiff(text1, text2) {
    // Replace null by an empty string
    text1 = text1 || ""
    text2 = text2 || ""

    if (!_.isString(text1) || !_.isString(text2)) {
        throw Error("text1 and text2 should be strings")
    }

    text1 = text1.replace(/\r\n/g, "\n").replace(/\r/g, "\n")
    text2 = text2.replace(/\r\n/g, "\n").replace(/\r/g, "\n")

    let wordArray = [] // e.g. lineArray[4] == "Hello\n"
    let wordHash = {} // e.g. lineHash["Hello\n"] == 4

    // "\x00" is a valid character, but various debuggers don't like it.
    // So we'll insert a junk entry to avoid generating a null character.
    wordArray.push("")

    let chars1 = diff_wordsToCharsMunge(text1, wordArray, wordHash)
    let chars2 = diff_wordsToCharsMunge(text2, wordArray, wordHash)

    let diffs = diffMatchPatch.diff_main(chars1, chars2, false)
    diffMatchPatch.diff_charsToLines_(diffs, wordArray)
    diffMatchPatch.diff_cleanupSemantic(diffs)
    return diffs
}

function formatDiff(diffs, { withInsertions = true, withDeletion = true } = {}) {
    let outputMorcels = []

    for (let diff of diffs) {
        let [operation, text] = diff

        if (text == "") {
            continue
        }

        if (operation == -1 && withDeletion) {
            outputMorcels.push(`<del>${text}</del>`)
        } else if (operation == 1 && withInsertions) {
            outputMorcels.push(`<ins>${text}</ins>`)
        } else if (operation == 0) {
            outputMorcels.push(text)
        }
    }

    return outputMorcels.join("").replace(/\n/g, "\u00b6\n")
}

export { textDiff, formatDiff }
