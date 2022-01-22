<template>
<div class="VuePDFjs">
    <Spinner v-if="loading" />
    <div ref="viewerContainer">
        <div
            id="viewer"
            class="pdfViewer"
        ></div>
    </div>
</div>
</template>

<script>
// READ
//https://pspdfkit.com/blog/2018/render-pdfs-in-the-browser-with-pdf-js/
// https://www.sitepoint.com/custom-pdf-rendering/

import _ from "lodash"
import $ from "jquery"
let pdfjsLib = require("pdfjs-dist")
let pdfjsViewer = require("pdfjs-dist/web/pdf_viewer")
import PilotMixin from "@components/PilotMixin"

// Webpack is configured to output this separate file for the pdf.js worker ( see webpack.config.js )
pdfjsLib.GlobalWorkerOptions.workerSrc = "/static/pdf.worker.js"

// Some PDFs need external cmaps.
const CMAP_URL = "pdfjs-dist/cmaps/"
const CMAP_PACKED = true

export default {
    name: "VuePDFjs",
    mixins: [PilotMixin],
    props: {
        pdfpath: {
            type: String,
            required: true,
        },
    },
    data: () => ({
        loading: false,
    }),
    mounted() {
        this.loading = true

        // Start loading the document the sooner possible
        let loadingTask = pdfjsLib.getDocument({
            url: this.pdfpath,
            cMapUrl: CMAP_URL,
            cMapPacked: CMAP_PACKED,
        })

        let container = this.$refs.viewerContainer

        // (Optionally) enable hyperlinks within PDF files.
        let pdfLinkService = new pdfjsViewer.PDFLinkService()

        // (Optionally) enable find controller.
        let pdfFindController = new pdfjsViewer.PDFFindController({
            linkService: pdfLinkService,
        })

        let pdfViewer = new pdfjsViewer.PDFViewer({
            container: container,
            linkService: pdfLinkService,
            findController: pdfFindController,
        })
        pdfLinkService.setViewer(pdfViewer)

        let pageWidth = 1
        function getScale() {
            return Math.min(1, $(container).innerWidth() / pageWidth)
        }
        this.scheduleRescale = _.throttle(() => {
            pdfViewer.currentScale = getScale()
        }, 50)
        this.onPageInit = () => {
            pageWidth = pdfViewer.getPageView(0).width
            this.scheduleRescale()
        }

        $(document).on("pagesinit", this.onPageInit)
        $(window).on("resize", this.scheduleRescale)

        loadingTask.promise
            .then((pdfDocument) => {
                // Document loaded, specifying document for the viewer and
                // the (optional) linkService.
                pdfViewer.setDocument(pdfDocument)
                pdfLinkService.setDocument(pdfDocument, null)
            })
            .finally(() => {
                this.loading = false
            })
    },
    beforeDestroy() {
        $(document).off("pagesinit", this.onPageInit)
        $(window).off("resize", this.scheduleRescale)
    },
}
</script>

<style lang="scss">
@import "~pdfjs-dist/web/pdf_viewer.css";

// This is required to correctly resize the pdf viewer on window resize
.VuePDFjs {
    width: 100%;
}

// Override pdfjs default css
.pdfViewer .page {
    border-image: url(/static/shadow.png) 9 9 repeat;
}
/*.pdfViewer .page .loadingIcon {
    background: none;
}*/
</style>
