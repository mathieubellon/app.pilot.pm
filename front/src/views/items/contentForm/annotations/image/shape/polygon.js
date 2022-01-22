import { Rectangle } from "./rectangle"
import { Point } from "./point"

/**
 * A polygon.
 * @param {Array.<Point>} points the points
 * @constructor
 */
export class Polygon {
    constructor({ points }) {
        this.points = points
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
        let points = this.points
        let inside = false

        let j = points.length - 1
        for (let i = 0; i < points.length; i++) {
            if (
                points[i].y > py != points[j].y > py &&
                px <
                    ((points[j].x - points[i].x) * (py - points[i].y)) /
                        (points[j].y - points[i].y) +
                        points[i].x
            ) {
                inside = !inside
            }
            j = i
        }

        return inside
    }

    /**
     * Returns the size of a shape.
     * @return {number} the size
     */
    getSize() {
        return Math.abs(this.computeArea(this.points))
    }

    /**
     * Returns the bounding rectangle of a shape.
     * @return {Rectangle} the bounding rectangle
     */
    getBoundingRect() {
        let points = this.points

        let left = points[0].x
        let right = points[0].x
        let top = points[0].y
        let bottom = points[0].y

        for (let i = 1; i < points.length; i++) {
            if (points[i].x > right) right = points[i].x

            if (points[i].x < left) left = points[i].x

            if (points[i].y > bottom) bottom = points[i].y

            if (points[i].y < top) top = points[i].y
        }

        return new Rectangle({
            x: left,
            y: top,
            width: right - left,
            height: bottom - top,
        })
    }

    /**
     * Computes the centroid coordinate for the specified shape.
     * @returns {geom.Point | undefined} the centroid X/Y coordinate
     */
    getCentroid() {
        return this.computeCentroid(this.points)
    }

    /**
     * Expands a shape by a specified delta.
     * @param {number} delta the delta
     */
    expand(delta) {
        return new Polygon({
            points: this.expandPolygon(this.points, delta),
        })
    }

    /** Polygon-specific helper functions & geometry computation utilities **/

    /**
     * Computes the area of a polygon. Note that the area can be <0, depending on the
     * clockwise/counterclockwise orientation of the polygon vertices!
     * @param {Array.<Point>} points the points
     * @return {number} the area
     */
    computeArea(points) {
        let area = 0.0

        let j = points.length - 1
        for (let i = 0; i < points.length; i++) {
            area += (points[j].x + points[i].x) * (points[j].y - points[i].y)
            j = i
        }

        return area / 2
    }

    /**
     * Tests if a polygon is oriented clockwise or counterclockwise.
     * @param {Array.<Point>} points the points
     * @return {boolean} true if the geometry is in clockwise orientation
     */
    isClockwise(points) {
        return this.computeArea(points) < 0
    }

    /**
     * Computes the centroid coordinate of a polygon.
     * @param {Array.<Point>} points the points
     * @returns {Point} the centroid X/Y coordinate
     */
    computeCentroid(points) {
        let x = 0
        let y = 0
        let f
        let j = points.length - 1

        for (let i = 0; i < points.length; i++) {
            f = points[i].x * points[j].y - points[j].x * points[i].y
            x += (points[i].x + points[j].x) * f
            y += (points[i].y + points[j].y) * f
            j = i
        }

        f = this.computeArea(points) * 6
        return new Point(Math.abs(x / f), Math.abs(y / f))
    }

    /**
     * A simple triangle expansion algorithm that shifts triangle vertices in/outwards by a specified
     * delta, along the axis centroid->vertex. Used internally as a subroutine for polygon expansion.
     * @param {Array.<Point>} points the points
     * @return {Array.<Point>} the expanded triangle
     * @private
     */
    _expandTriangle(points, delta) {
        function signum(number) {
            return number > 0 ? 1 : number < 0 ? -1 : 0
        }

        function shiftAlongAxis(px, centroid, delta) {
            let axis = { x: px.x - centroid.x, y: px.y - centroid.y }
            let sign_delta = signum(delta)
            let sign_x = signum(axis.x) * sign_delta
            let sign_y = signum(axis.y) * sign_delta

            let dy = Math.sqrt(Math.pow(delta, 2) / (1 + Math.pow(axis.x / axis.y, 2)))
            let dx = (axis.x / axis.y) * dy
            return { x: px.x + Math.abs(dx) * sign_x, y: px.y + Math.abs(dy) * sign_y }
        }

        let centroid = this.computeCentroid(points)
        let expanded = []

        for (let i = 0; i < points.length; i++) {
            let sign = this.isClockwise(points) ? -1 : 1
            expanded.push(shiftAlongAxis(points[i], centroid, sign * delta))
        }

        return expanded
    }

    /**
     * A simple polygon expansion algorithm that generates a series of triangles from
     * the polygon, and then subsequently applies the _expandTriangle method.
     * @param {Array.<Point>} points the points
     * @param {number} delta the distance by which to expand
     * @return {Array.<Point>} the expanded polygon
     */
    expandPolygon(points, delta) {
        let sign = this.isClockwise(points) ? -1 : 1

        if (points.length < 4) return this._expandTriangle(points, sign * delta)

        let prev = points.length - 1
        let next = 1

        let expanded = []
        for (let current = 0; current < points.length; current++) {
            let expTriangle = this._expandTriangle(
                [points[prev], points[current], points[next]],
                sign * delta,
            )
            expanded.push(expTriangle[1])
            prev = current
            next++
            if (next > points.length - 1) next = 0
        }

        return expanded
    }
}
