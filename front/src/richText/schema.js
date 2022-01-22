import _ from "lodash"
import { DOMSerializer as ProsemirrorDOMSerializer } from "prosemirror-model"
import { defaultMarkdownSerializer } from "prosemirror-markdown"
import { Editor } from "tiptap"
import {
    // Nodes
    Blockquote,
    BulletList,
    CodeBlock,
    HardBreak,
    Heading,
    HorizontalRule,
    ListItem,
    OrderedList,
    // Marks
    Code,
    Strike,
    Underline,
    //Table
    Table,
    TableHeader,
    TableCell,
    TableRow,
    // Plugins
    History,
    TrailingNode,
} from "tiptap-extensions"
import { Bold, Italic, Link, Image } from "./extensions/core"
import { Mention } from "./extensions/mentions"
import { Placeholder } from "./extensions/placeholder"
import { DiffAndMerge } from "./extensions/diffAndMerge"
import { HighlightRange } from "./extensions/highlightRange"
import { ImageUpload } from "./extensions/imageUpload"
import { Selection } from "./extensions/selection"
import { serializeNodeToHTML } from "@/richText/utils"

const EMPTY_PROSEMIRROR_DOC = { content: [{ type: "paragraph" }], type: "doc" }

// For execution in node.js for markdown export
class Mehditor extends Editor {
    init(options = {}) {
        this.setOptions({
            ...this.defaultOptions,
            ...options,
        })
        this.extensions = this.createExtensions()
        this.nodes = this.createNodes()
        this.marks = this.createMarks()
        this.schema = this.createSchema()
    }
}

const defaultFeatures = {
    image: true,
    mention: true,
    table: true,
}

function getExtensionsPrivate(features) {
    let extensions = [
        // Nodes
        new Blockquote(),
        new BulletList(),
        new CodeBlock(),
        new HardBreak(),
        new Heading(),
        new HorizontalRule(),
        new ListItem(),
        new OrderedList(),

        // Marks
        new Bold(),
        new Code(),
        new Italic(),
        new Link(),
        new Strike(),
        new Underline(),

        // Plugins
        new DiffAndMerge(),
        new HighlightRange(),
        new History(),
        new Placeholder(),
        new TrailingNode({
            node: "paragraph",
            notAfter: ["paragraph"],
        }),
        new Selection(),
    ]

    if (features.image) {
        extensions.push(new Image())
        extensions.push(new ImageUpload())
    }
    if (features.mention) {
        extensions.push(new Mention())
    }
    if (features.table) {
        extensions.push(new Table(), new TableHeader(), new TableCell(), new TableRow())
    }

    return extensions
}

function buildSchema(features) {
    features = _.defaults(features, defaultFeatures)
    let getExtensions = () => getExtensionsPrivate(features)

    let prosemirrorSchema = new Mehditor({ extensions: getExtensions() }).schema
    let DOMSerializer = ProsemirrorDOMSerializer.fromSchema(prosemirrorSchema)
    let MarkdownSerializer = defaultMarkdownSerializer

    // We remove the <p> inside the <li> elements
    DOMSerializer.nodes.list_item = function (node) {
        let contentNodes = node.content.content
        // If the <li> has a single paragraph child, then we skip the <p> element and render directly its content
        if (contentNodes.length == 1 && contentNodes[0].type.name == "paragraph") {
            return ["li", DOMSerializer.serializeFragment(contentNodes[0].content)]
        }
        // Other cases : standard DOMOutputSpec
        else {
            return ["li", 0]
        }
    }

    // During serialization, we add a target '_blank' to avoid an exit of the working context
    DOMSerializer.marks.link = (node) => [
        "a",
        {
            href: node.attrs.href,
            title: node.attrs.title,
            target: "_blank",
        },
        0,
    ]

    // There's not syntax for underline, strike and mentions in markdown, do nothing
    MarkdownSerializer.marks.underline = MarkdownSerializer.marks.strike = MarkdownSerializer.marks.mention = {
        open: "",
        close: "",
    }

    // There is a extension syntax for tables in markdown, but it's not widely supported.
    // Go for the safe path with embedded html
    MarkdownSerializer.nodes.table = (state, node) => {
        state.ensureNewLine()
        state.write("<table>\n")
        state.write(serializeNodeToHTML(node, DOMSerializer, "\n"))
        state.ensureNewLine()
        state.write("</table>\n")
        state.closeBlock(node)
    }

    let nodeFromJSON = prosemirrorSchema.nodeFromJSON
    function HTMLFromJSON(json) {
        if (!json || _.isEmpty(json)) return ""

        return serializeNodeToHTML(prosemirrorSchema.nodeFromJSON(json), DOMSerializer)
    }
    function textFromJSON(json) {
        if (!json || _.isEmpty(json)) return ""
        return prosemirrorSchema.nodeFromJSON(json).textContent
    }

    return {
        getExtensions,
        prosemirrorSchema,
        DOMSerializer,
        MarkdownSerializer,
        nodeFromJSON,
        HTMLFromJSON,
        textFromJSON,
    }
}

let fullSchema = buildSchema()
let richTextSchema = buildSchema({ mention: false, image: false, table: false })
let itemContentSchema = buildSchema({ mention: false })
let commentSchema = buildSchema({ image: false, table: false })
// This is the same than itemContentSchema, but we better be future-proof here.
let wikiSchema = buildSchema({ mention: false })

export {
    fullSchema,
    richTextSchema,
    itemContentSchema,
    commentSchema,
    wikiSchema,
    EMPTY_PROSEMIRROR_DOC,
}
