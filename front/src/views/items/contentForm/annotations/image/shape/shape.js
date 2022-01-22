import { Rectangle } from "./rectangle"
import { Polygon } from "./polygon"

/**
 * Possible shape types
 * @enum {string}
 */
export const ShapeType = {
    POINT: "point",
    RECTANGLE: "rect",
    POLYGON: "polygon",
}

/**
 * Geometries
 * @enum
 */
export const Geometries = {
    [ShapeType.RECTANGLE]: Rectangle,
    [ShapeType.POLYGON]: Polygon,
}

/**
 * Possible unit types
 * @enum {string}
 */
export const Units = {
    PIXEL: "pixel",
    FRACTION: "fraction",
}

/**
 * A shape. Consists of descriptive shape metadata, plus the actual shape geometry.
 * @param {ShapeType} type the shape type
 * @param {geom.Point | geom.Rectangle | geom.Polygon} geometry the geometry
 * @param {Units=} units geometry measurement units
 * @param {Object} drawing style of the shape (optional)
 * @constructor
 */
export class Shape {
    constructor({ type, geometry, pixelGeometry, units, style }) {
        this.type = type
        this.geometry = geometry
        // The viewer always operates in pixel coordinates for efficiency reasons
        this.pixelGeometry = pixelGeometry
        if (units) this.units = units
        if (style) this.style = style
        else this.style = {}
    }

    static fromAnnotation(annotation, annotator) {
        let type = annotation.shape.type
        let GeometryClass = Geometries[type]
        let geometry = new GeometryClass(annotation.shape.geometry)

        // The viewer always operates in pixel coordinates for efficiency reasons
        // Convert fractions to pixels at init
        let pixelGeometry = geometry
        if (annotation.shape.units != Units.PIXEL) {
            pixelGeometry = geometry.toPixelCoordinates(annotator.imageWidth, annotator.imageHeight)
        }

        return new Shape({
            type,
            geometry: geometry,
            pixelGeometry: pixelGeometry,
            units: annotation.shape.units,
            style: annotation.shape.style,
        })
    }
}
