import { Mark } from "tiptap"

export class Mention extends Mark {
    get name() {
        return "mention"
    }

    get schema() {
        return {
            attrs: {
                entity: { default: null },
                id: { default: null },
                uid: { default: null },
            },
            inclusive: false,
            toDOM: (node) => [
                "span",
                {
                    entity: node.attrs.entity,
                    id: node.attrs.id,
                    class: "mention " + node.attrs.entity,
                },
                0,
            ],
        }
    }
}
