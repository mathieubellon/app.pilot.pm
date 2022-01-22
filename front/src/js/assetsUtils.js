import _ from "lodash"
import urls from "@js/urls"
import { $http } from "@js/ajax"

const SIGNATURE_URL = urls.assetsGetS3Signature.format()

export function getFileProperties(file) {
    return {
        file: file.policy.key,
        fileName: file.name,
        uuid: file.policy.uuid,
        mime: file.type,
        height: _.has(file, "height") ? file.height : null,
        width: _.has(file, "width") ? file.width : null,
        size: file.size,
    }
}

export function signFileForAssetUpload(file, assetId) {
    let fileInfo = {
        fileName: file.name,
        size: file.size,
        contentType: file.type,
        assetId: assetId,
    }
    /* Signature for Ireland AWS Region */
    return $http.post(SIGNATURE_URL, fileInfo).then((response) => {
        file.assetId = response.data.assetId
        delete response.data.assetId
        file.policy = response.data
        return file
    })
}

export function getImageAttrsFromAsset(asset) {
    // We chose which image to use in the editor,
    // depending on the width of the original image file.
    // Uploaded images are converted by transloadit to a 1000px-width version
    // in the "working urls" array.
    // If the original image is less wide than 1000px, the working url will be aliased.
    // If the original image is wider than 1000px, that means it can be quite heavy.
    let src
    // Here, take the original to avoid aliasing
    if (asset.width < 1000) {
        src = asset.file_url
    }
    // Here, take the resized image to prevent loading a fat file
    else {
        let firstWorkingUrl = _.get(asset, "working_urls.0", null)
        src = firstWorkingUrl ? firstWorkingUrl : asset.cover_url
    }

    return {
        src: src,
        caption: asset.html_caption,
        title: asset.html_title,
        alt: asset.html_alt,
    }
}
