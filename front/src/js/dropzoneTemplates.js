const DZ_PREVIEW_TEMPLATE_WITH_IMAGE = (options) => `
    <div class="AssetElement GridView">
        <div class="AssetPreview uploadInProgress">
            <img data-dz-thumbnail />
        </div>
        <div class="AssetElement__Title"><span data-dz-name></span>[ <span data-dz-size></span> ]</div>
        <div class="AssetElement__Progress"><span class="AssetElement__PercentUpload" data-dz-uploadprogress></span></div>
        <div class="AssetElement__Error"><span data-dz-errormessage></span></div>
    </div>
`

const DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE = (options) => `
    <div class="AssetElement ListWithoutImage">
        <div class="AssetElement__Title"><span data-dz-name></span>[ <span data-dz-size></span> ]</div>
        <div class="AssetElement__Progress"><span class="AssetElement__PercentUpload" data-dz-uploadprogress></span></div>
        <div class="AssetElement__Error"><span data-dz-errormessage></span></div>
    </div>
`

const DZ_PREVIEW_TEMPLATE_RICH_TEXT_UPLOADING = (options) => `
    <div class="AssetElement GridView m-0">
        <div class="AssetPreview uploadInProgress">
            <img data-dz-thumbnail />
        </div>
        <div class="AssetElement__Title"><span data-dz-name></span>[ <span data-dz-size></span> ]</div>
        <div class="AssetElement__Progress"><span class="AssetElement__PercentUpload" data-dz-uploadprogress></span></div>
        <div class="AssetElement__Error"><span data-dz-errormessage></span></div>
    </div>
`

export {
    DZ_PREVIEW_TEMPLATE_WITH_IMAGE,
    DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE,
    DZ_PREVIEW_TEMPLATE_RICH_TEXT_UPLOADING,
}
