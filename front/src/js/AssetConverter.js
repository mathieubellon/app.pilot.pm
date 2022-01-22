import urls from "@js/urls"
import { $httpX } from "@js/ajax"
import Emitter from "@js/Emitter"
import { mainApp } from "@js/bootstrap"
import realtime from "@js/realtime"

export default class AssetConverter extends Emitter {
    constructor() {
        super()

        this.documentTitle = document.title
    }

    startConversion(asset) {
        $httpX({
            name: "startConversion",
            commit: mainApp.$store.commit,
            url: urls.assetsStartConversion.format({ id: asset.id }),
            method: "POST",
        }).then((response) => {
            let asset = response.data
            this.emit("conversionStatusUpdate", asset)
            this.waitForAssetConversionStatus(asset)
        })
    }

    waitForAssetConversionStatus(asset) {
        realtime.addMessageHandler(
            realtime.S2C_MESSAGES.BROADCAST_ASSET_CONVERSION_STATUS,
            (message) => {
                if (message.asset.id == asset.id) {
                    this.emit("conversionStatusUpdate", message.asset)
                }
            },
        )
        realtime.connect()
    }

    onTotalUploadProgress(uploadProgress) {
        document.title =
            uploadProgress === 100
                ? this.documentTitle
                : Math.round(uploadProgress) + "% - " + this.documentTitle
    }
}
