import { EMPTY_PROSEMIRROR_DOC, getProsemirrorContent } from "./fixtures/prosemirror"
const JSONSortify = require("json.sortify")

let itemUIState
let $compile, $scope
let annotationManager

let AnnotationsManagerMock = jest.fn(() => {
    annotationManager = {
        annotations: {},
        setPmView: jest.fn(),
        setAnnotations: jest.fn(),
    }
    return annotationManager
})

beforeEach(() => {
    itemUIState = {
        itemReadOnly: {},
    }
    annotationManager = null
    AnnotationsManagerMock.mockClear()
})

beforeEach(inject(function (_$compile_, $rootScope) {
    // Reference to the compile service
    $compile = _$compile_

    // Testing scope
    $scope = $rootScope.$new()
}))

mockCommonRequests()

test.skip("exists", () => {
    let pmElement = $compile("<prosemirror></prosemirror>")($scope)
    $scope.$apply()

    let pmHtml = pmElement.html()
    expect(pmHtml).toContain('class="ProseMirror"')
    expect(pmHtml).toContain('contenteditable="true"')
    expect(pmHtml).toContain('<p class="empty empty-doc"><br></p>')
    expect(pmHtml).toContain('class="ProseMirror-tooltip"')
    expect(pmHtml).toContain("ProseMirror-tooltip-pointer")

    expect(AnnotationsManagerMock.mock.instances.length).toBe(1)
    expect(annotationManager.setPmView).toHaveBeenCalled()
})

test.skip("with ng-model", () => {
    $scope.content = EMPTY_PROSEMIRROR_DOC
    $compile("<prosemirror ng-model='content'></prosemirror>")($scope)
    $scope.$apply()

    expect($scope.content).toBeDefined()
    expect($scope.content).toEqual(EMPTY_PROSEMIRROR_DOC)
})

test.skip("initial content", () => {
    let initialContent = JSONSortify(getProsemirrorContent("meh"))
    $compile("<prosemirror ng-model='content'>" + initialContent + "</prosemirror>")($scope)
    $scope.$apply()

    expect($scope.content).toBeDefined()
    expect($scope.content).toEqual(initialContent)
})

test.skip("with pmApi", () => {
    $compile("<prosemirror pm-api='pmApi'></prosemirror>")($scope)
    $scope.$apply()

    let pmApi = $scope.pmApi
    expect(pmApi).toBeDefined()
    expect(pmApi.pmView).toBeDefined()
    expect(pmApi.annotationManager).toBeDefined()
    expect(pmApi.renderContent).toBeDefined()
})

test.skip("content update", () => {
    let pmElement = $compile("<prosemirror ng-model='content'></prosemirror>")($scope)
    $scope.$apply()

    let pmHtml = pmElement.html()
    expect(pmHtml).toContain('<p class="empty empty-doc"><br></p>')

    $scope.content = JSONSortify(getProsemirrorContent("meh"))
    $scope.$apply()

    pmHtml = pmElement.html()
    expect(pmHtml).toContain('<p class="">meh</p>')
})

test.skip("with initial annotations", () => {
    itemUIState.itemReadOnly.annotations = { 1: {} }
    $scope.content = getProsemirrorContent("meh")

    $compile("<prosemirror ng-model='content' pm-api='pmApi'></prosemirror>")($scope)
    $scope.$apply()
    $scope.pmApi.renderContent()

    expect(AnnotationsManagerMock.mock.instances.length).toBe(1)
    expect(annotationManager.setAnnotations).toHaveBeenCalled()
})
