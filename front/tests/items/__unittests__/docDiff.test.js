import { ReplaceStep } from "prosemirror-transform/dist"

import DocDiff from "../content_form/prosemirror/docDiff"
import pilotSchema from "../content_form/prosemirror/itemContentSchema"
import _ from "lodash"

let smallDocLeft = {
    content: [{ content: [{ text: "a b c", type: "text" }], type: "paragraph" }],
    type: "doc",
}

test("exists", () => {
    expect(DocDiff).toBeDefined()
})

test("do simple diff", () => {
    let smallDocRight = _.cloneDeep(smallDocLeft)
    smallDocRight.content[0].content[0].text = "a MEH c"
    let docDiff = new DocDiff(
        pilotSchema.nodeFromJSON(smallDocLeft),
        pilotSchema.nodeFromJSON(smallDocRight),
    )

    expect(docDiff).toBeDefined()
    expect(docDiff.isInverted).toBeFalsy()
    expect(docDiff.deltaList.length).toBe(4) // Four delta parts : two unchanged, one add, one remove
    expect(docDiff.changes.length).toBe(1) // One change

    // We expect to find a delta list equals to :
    // [ [0, "OPEN_NODEa "], [-1, "b "], [1, "MEH "], [0, "cCLOSE_NODE"]]
    expect(docDiff.deltaList.map((delta) => delta[0])).toEqual([0, -1, 1, 0])
    expect(docDiff.deltaList.map((delta) => delta[1])).toEqual([
        "\u0011a ",
        "b ",
        "MEH ",
        "c\u0012",
    ])
    expect(docDiff.deltaList.map((delta) => delta[1].startPos)).toEqual([0, 3, 3, 7])

    let change = docDiff.changes[0]
    expect(change.step).toBeDefined()
    expect(change.step).toBeInstanceOf(ReplaceStep)
    expect(change.step.from).toBe(3)
    expect(change.step.to).toBe(5)
    expect(change.step.slice).toEqual(change.sliceAdded)
    expect(change.sliceAdded.content.childCount).toBe(1)
    expect(change.sliceAdded.content.firstChild.text).toBe("MEH ")
    expect(change.sliceAdded.toJSON()).toEqual({ content: [{ text: "MEH ", type: "text" }] })
    expect(change.sliceRemoved.content.childCount).toBe(1)
    expect(change.sliceRemoved.content.firstChild.text).toBe("b ")
    expect(change.sliceRemoved.toJSON()).toEqual({ content: [{ text: "b ", type: "text" }] })
    expect(change.getDeletedText()).toBe("b")
    expect(change.getAddedText()).toBe("MEH")
})

test("diff with marks", () => {
    let smallDocRight = {
        content: [
            {
                content: [
                    { text: "a ", type: "text" },
                    { text: "b ", type: "text", marks: [{ type: "strong" }] },
                    { text: "c", type: "text" },
                ],
                type: "paragraph",
            },
        ],
        type: "doc",
    }
    let docDiff = new DocDiff(
        pilotSchema.nodeFromJSON(smallDocLeft),
        pilotSchema.nodeFromJSON(smallDocRight),
    )

    let change = docDiff.changes[0]
    expect(change.step.from).toBe(3)
    expect(change.step.to).toBe(5)
    expect(change.sliceAdded.content.childCount).toBe(1)
    expect(change.sliceAdded.content.firstChild.text).toBe("b ")
    expect(change.sliceAdded.toJSON()).toEqual({
        content: [{ text: "b ", type: "text", marks: [{ type: "strong" }] }],
    })
    expect(change.getDeletedText()).toBe("b")
    expect(change.getAddedText()).toBe("b")
})
