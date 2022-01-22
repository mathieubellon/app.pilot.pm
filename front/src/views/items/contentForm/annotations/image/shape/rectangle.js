import { Point } from "./point.js"

/**
 * A rectangle.
 * @param {number} x the anchor point x coordinate
 * @param {number} y the anchor point y coordinate
 * @param {number} width the rectangle width
 * @param {number} height the rectangle height
 * @constructor
 */
export class Rectangle {
    constructor({ x, y, width, height }) {
        if (width > 0) {
            this.x = x
            this.width = width
        } else {
            this.x = x + width
            this.width = -width
        }

        if (height > 0) {
            this.y = y
            this.height = height
        } else {
            this.y = y + height
            this.height = -height
        }
    }

    /**
     * Returns a new Rectangle where the coordinates are converted
     * from a fraction units (storage system) to a pixel units (viewport system)
     */
    toPixelCoordinates(imageWidth, imageHeight) {
        return new Rectangle({
            x: this.x * imageWidth,
            y: this.y * imageHeight,
            width: this.width * imageWidth,
            height: this.height * imageHeight,
        })
    }

    /**
     * Returns a new Rectangle where the coordinates are converted
     * from a pixel (viewport system) units to a fraction units (storage system)
     */
    toFractionCoordinates(imageWidth, imageHeight) {
        return new Rectangle({
            x: this.x / imageWidth,
            y: this.y / imageHeight,
            width: this.width / imageWidth,
            height: this.height / imageHeight,
        })
    }

    /**
     * Checks whether a given shape intersects a point.
     * @param {number} px the X coordinate
     * @param {number} py the Y coordinate
     * @return {boolean} true if the point intersects the shape
     */
    intersects(coords) {
        let px = coords.x,
            py = coords.y
        if (px < this.x) return false

        if (py < this.y) return false

        if (px > this.x + this.width) return false

        if (py > this.y + this.height) return false

        return true
    }

    /**
     * Returns the size of a shape.
     * @return {number} the size
     */
    getSize() {
        return this.width * this.height
    }

    /**
     * Returns the bounding rectangle of a shape.
     * @return {Rectangle} the bounding rectangle
     */
    getBoundingRect() {
        return this
    }

    /**
     * Returns a bounding rectangle object,
     * in a format compatible with the getBoundingClientRect native function :
     * {top, right, bottom, left, width, height}.
     *
     * @return {Rectangle} the bounding rectangle
     */
    getViewportBoundingRect() {
        return {
            left: this.x,
            top: this.y,
            right: this.x + this.width,
            bottom: this.y + this.height,
            width: this.width,
            height: this.height,
        }
    }

    /**
     * Computes the centroid coordinate for the specified shape.
     * @returns {Point} the centroid X/Y coordinate
     */
    getCentroid() {
        return new Point(this.x + this.width / 2, this.y + this.height / 2)
    }

    /**
     * Translate a bounding rect into another coordinate system
     * ( used to move between local image coordinates VS viewport system )
     */
    translate(left, top) {
        return new Rectangle({
            x: this.x + left,
            y: this.y + top,
            width: this.width,
            height: this.height,
        })
    }

    /**
     * Expands a shape by a specified delta.
     * @param {number} delta the delta
     */
    expand(delta) {
        // TODO for the sake of completeness: implement for RECTANGLE
        return null
    }
}
