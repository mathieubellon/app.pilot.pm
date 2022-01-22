import $ from "jquery"
import _ from "lodash"
import Vue from "vue"
import { required } from "vuelidate/lib/validators"
import { createFieldValidation, createFieldWarning } from "@js/validation.js"
import PopperUtils from "popper.js/dist/esm/popper-utils.js"
import { mainApp } from "@js/bootstrap"

function getItemScrollableContainer() {
    return $(PopperUtils.getScrollParent($(".CenterPane")[0]))
}

function getCurrentItemScroll() {
    return getItemScrollableContainer().scrollTop()
}

function scrollItemTo({
    topCoord = null,
    $elem = null,
    offset = 0,
    adjustEditionPanel = false,
    adjustCurrentScroll = false,
}) {
    if ($elem) {
        topCoord = $elem.offset().top
    }

    // Jquery refs to DOM containers
    let $scrollableContainer = getItemScrollableContainer()
    let finalCoord = topCoord - offset
    if (adjustEditionPanel) {
        let editionPanel = $(".ItemDetailBody")
        if (!editionPanel.length) {
            editionPanel = $(".SharingApp__body")
        }
        finalCoord -= editionPanel.offset().top
    }
    if (adjustCurrentScroll) {
        finalCoord += $scrollableContainer.scrollTop()
    }
    $scrollableContainer.scrollTop(finalCoord)
}

/**
 * Reposition things on the ItemDetail page, when the viewport is moving :
 * 1/ On window resize
 * 2/ On item center pane scroll
 * 3/ On right menu opening/ closing
 */
class ItemPositioner {
    constructor(namespace, redrawCallback) {
        this.namespace = namespace
        this.eventAttached = false
        this.$scrollParent = getItemScrollableContainer()
        this.callbacks = {
            onWindowResize: redrawCallback,
            onScroll: redrawCallback,
            onDrawerTransition: redrawCallback,
        }
        this.attachEventHandlers()
    }

    attachEventHandlers() {
        // Re-render on window resize
        $(window).on("resize." + this.namespace, () => this.callbacks.onWindowResize())
        // Re-render on center pane scroll
        this.$scrollParent.on("scroll." + this.namespace, () => this.callbacks.onScroll())
        // Re-render during right menu open/close
        let renderIntervalId = null
        let stopDrawerTransitionInterval = () => {
            if (renderIntervalId) {
                clearInterval(renderIntervalId)
                renderIntervalId = null
                this.callbacks.onDrawerTransition()
            }
        }
        $(document).on(
            "transitionstart." + this.namespace,
            ".ItemRightMenu__drawer__element",
            () => {
                // Cancel previous interval if needed
                if (renderIntervalId) {
                    clearInterval(renderIntervalId)
                }

                renderIntervalId = setInterval(this.callbacks.onDrawerTransition, 15)
                // Ensure that we don't keep the interval running indefinitely
                setTimeout(stopDrawerTransitionInterval, 1000)
            },
        )
        $(document).on(
            "transitionend." + this.namespace,
            ".ItemRightMenu__drawer__element",
            stopDrawerTransitionInterval,
        )
        this.eventAttached = true
    }

    /**
     * Remove all event handler
     */
    detachEventHandlers() {
        $(document).off("transitionstart." + this.namespace)
        $(document).off("transitionend." + this.namespace)
        $(window).off("resize." + this.namespace)
        this.$scrollParent.off("scroll." + this.namespace)
        this.eventAttached = false
    }
}

function getElasticFieldName(fieldSchema, index) {
    if (index > 0) return `${fieldSchema.name}-${index}`
    else return fieldSchema.name
}

function getElasticFieldSize(fieldSchema, content) {
    let i = 1 // Elastic size cannot be less than one
    while (_.has(content, getElasticFieldName(fieldSchema, i))) {
        i++
    }
    return i
}

/**
 * Generate the elastic schemas for a single field schema.
 */
function getElasticFieldSchemas(fieldSchema, content) {
    let schemas = []
    for (let i = 0; i < getElasticFieldSize(fieldSchema, content); i++) {
        let schema = _.cloneDeep(fieldSchema)
        schema.name = getElasticFieldName(schema, i)
        schema.label = `${schema.label} (${i + 1})`
        schemas.push(schema)
    }
    return schemas
}

/**
 * Generate all field schemas for a content schema, taking into account the elastic fields, expanding them as needed.
 */
function getAllFieldSchemas(contentSchema, content) {
    let schemas = []
    for (let fieldSchema of contentSchema) {
        if (fieldSchema.elastic) {
            schemas = [...schemas, ...getElasticFieldSchemas(fieldSchema, content)]
        } else {
            schemas.push(fieldSchema)
        }
    }
    return schemas
}

function createItemValidation(contentSchema, metadataSchema, item) {
    let validator = new Vue({
        data: item,
        validations() {
            let validations = {
                content: {},
            }

            /** Build content validation **/
            for (let fieldSchema of contentSchema) {
                if (fieldSchema.elastic) {
                    for (let i = 0; i < getElasticFieldSize(fieldSchema, item.content); i++) {
                        validations.content[
                            getElasticFieldName(fieldSchema, i)
                        ] = createFieldValidation(fieldSchema)
                    }
                } else {
                    validations.content[fieldSchema.name] = createFieldValidation(fieldSchema)
                }
            }
            /** Build metadata validation **/
            const RELATED_FIELD_NAMES = [
                "channels",
                "owners",
                "project",
                "targets",
                "workflow_state",
            ]
            _.forEach(metadataSchema, (fieldSchema, fieldName) => {
                // Related fields uses their '_id' suffixed name for write operations.
                // Validation must be done on this suffixed name.
                if (RELATED_FIELD_NAMES.indexOf(fieldName) > -1) {
                    fieldName = fieldName + "_id"
                }

                let fieldValidation = {}
                if (fieldSchema.required) {
                    fieldValidation.required = required
                }
                validations[fieldName] = fieldValidation
            })

            return validations
        },
        created() {
            /**
             * Elastic content fields will add a new key to the item content (or remove an existing one)
             * Vue.js cannot make reactive watch on that, so here we simulate it
             * with a watch which force update when the key change.
             */
            this.unwatch = this.$watch(
                function () {
                    return Object.keys(this.content)
                },
                function () {
                    this.$v.$touch()
                    this.$forceUpdate()
                },
            )
        },
        beforeDestroy() {
            this.unwatch()
        },
    })

    // Creator of item validation must destroy the validation when not used anymore, to prevent memory leaks
    validator.$v.freeMemory = function () {
        validator.$destroy()
    }

    return validator.$v
}

function createItemWarnings(contentSchema, item) {
    let validator = new Vue({
        data: item,
        validations() {
            let warnings = {
                content: {},
            }

            /** Build content warnings **/
            for (let fieldSchema of contentSchema) {
                if (fieldSchema.elastic) {
                    for (let i = 0; i < getElasticFieldSize(fieldSchema, item.content); i++) {
                        warnings.content[getElasticFieldName(fieldSchema, i)] = createFieldWarning(
                            fieldSchema,
                        )
                    }
                } else {
                    warnings.content[fieldSchema.name] = createFieldWarning(fieldSchema)
                }
            }

            return warnings
        },
        created() {
            /**
             * Elastic content fields will add a new key to the item content (or remove an existing one)
             * Vue.js cannot make reactive watch on that, so here we simulate it
             * with a watch which force update when the key change.
             */
            this.unwatch = this.$watch(
                function () {
                    return Object.keys(this.content)
                },
                function () {
                    this.$v.$touch()
                    this.$forceUpdate()
                },
            )
        },
        beforeDestroy() {
            this.unwatch()
        },
    })

    // Creator of item validation must destroy the validation when not used anymore, to prevent memory leaks
    validator.$v.freeMemory = function () {
        validator.$destroy()
    }

    return validator.$v
}

/**
 * A function that enrich a light item :
 *  - add item.item_type from its corresponding item_type_id
 *  - add item.workflow_state from its corresponding workflow_state_id
 */
function enrichLightItem(item) {
    let state = mainApp.$store.state
    // Replace the item type id by the full representation.
    if (item.item_type_id && !item.item_type) {
        let itemType = _.find(state.itemTypes.itemTypes, {
            id: item.item_type_id,
        })
        // Not found, replace by an empty item_type
        if (!itemType) {
            itemType = {
                id: item.item_type_id,
                content_schema: [],
            }
        }
        Vue.set(item, "item_type", itemType)
    }

    // Replace the workflow state id by the full representation.
    if (item.workflow_state_id && !item.workflow_state) {
        let workflowState = _.find(state.workflow.workflowStates, {
            id: item.workflow_state_id,
        })
        if (workflowState) {
            Vue.set(item, "workflow_state", workflowState)
        }
    }
}

export {
    getCurrentItemScroll,
    scrollItemTo,
    ItemPositioner,
    createItemValidation,
    createItemWarnings,
    getElasticFieldName,
    getElasticFieldSize,
    getElasticFieldSchemas,
    getAllFieldSchemas,
    enrichLightItem,
}
