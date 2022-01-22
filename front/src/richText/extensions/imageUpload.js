import { Node } from "tiptap"
import ImageUploadView from "./ImageUploadView"

export class ImageUpload extends Node {
    get name() {
        return "imageUpload"
    }

    get schema() {
        return {
            inline: true,
            attrs: {
                uploadId: {},
                assetId: {
                    default: null,
                },
            },
            group: "inline",
            draggable: false,
            toDOM(node) {
                return ["div", { class: "ImageUploadView" }]
            },
        }
    }

    get view() {
        return ImageUploadView
    }
}
