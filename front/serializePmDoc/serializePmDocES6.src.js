/**
 * ES source for the prosemirrorJsonToMarkdown script.
 * Must be transpiled and bundled with webpack, from the front folder :
 * webpack --config serializePmDoc/serializePmDoc.webpack.config.js --mode production
 */
import {fullSchema} from '@richText/schema'
import { JSDOM } from 'jsdom'

const dom = new JSDOM('<!DOCTYPE html><div id="content"></div>')
const document = dom.window.document
const renderer = document.querySelector('div')

// Required for prosemirror internal serializeFragment
global.window = {document}

global.prosemirrorJsonToMarkdown = function(jsonDocument){
    return fullSchema.MarkdownSerializer.serialize(
        fullSchema.nodeFromJSON(jsonDocument)
    )
}

global.prosemirrorJsonToHTML = function(jsonDocument){
    fullSchema.DOMSerializer.serializeFragment(
        fullSchema.nodeFromJSON(jsonDocument), {document}, renderer
    )

    return document.getElementById('content').innerHTML
}

global.prosemirrorJsonToText = function(jsonDocument){
    let doc = fullSchema.nodeFromJSON(jsonDocument)
    return doc.textBetween(0, doc.content.size, '\n\n')
}
