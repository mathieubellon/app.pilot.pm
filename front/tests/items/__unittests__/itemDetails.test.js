import { getProsemirrorContent } from "./fixtures/prosemirror"

/***********************
 * Fake resource
 ************************/

const ITEM_ID = 1
const ITEM = {
    id: ITEM_ID,
    content: {
        title: "Title",
        body: getProsemirrorContent("meh"),
    },
}
const ITEM_VERSIONS = [
    {
        id: 1,
        version: "1.0",
        created_by: 1,
        created_at: "2017-01-01T08:00:00",
        restored_from_version: null,
        comment: "",
    },
]

/***********************
 * Controller mocking
 ************************/

function mockStateActions(StateActions) {
    for (let actionName in StateActions) {
        StateActions[actionName] = jest.fn()
    }
}

function getPmApiMock() {
    return {
        pmView: {},
        annotationManager: {},
        renderContent: () => {},
    }
}

// See https://docs.angularjs.org/guide/unit-testing
let itemCtrl, $httpBackend, $scope, itemUIState, reduxActions

beforeEach(inject(function (_$httpBackend_, $rootScope, $controller, StateActions) {
    // Mock Item ressource
    $httpBackend = _$httpBackend_

    // Testing scope
    $scope = $rootScope.$new()

    // Mock redux actions & item State
    mockStateActions(StateActions)
    reduxActions = StateActions
    itemUIState = { reduxActions: reduxActions }

    // Instanciate the test controller
    itemCtrl = $controller("ItemCtrl", {
        $scope: $scope,
        itemUIState: itemUIState,
    })
}))

mockCommonRequests()

afterEach(function () {
    $httpBackend.verifyNoOutstandingExpectation()
    $httpBackend.verifyNoOutstandingRequest()
})

function initItem() {
    $httpBackend.expectGET("/api/items/1/").respond(ITEM)
    $httpBackend.expectGET("/api/items/1/versions/").respond(ITEM_VERSIONS)
    itemCtrl.setItem(ITEM_ID)
    $scope.pmApi = getPmApiMock()
    $httpBackend.flush()
}

/***********************
 * Tests
 ************************/

test.skip("exists", () => {
    expect(itemCtrl).toBeDefined()
    expect($scope.itemUIState).toBe(itemUIState)
    expect(itemCtrl.itemContentForm).toBeNull()
    expect(itemCtrl.hasBody).toBeNull()

    // Just to validate verifyNoOutstandingRequest
    $httpBackend.flush()
})

test.skip("init item", () => {
    initItem()

    expect(itemUIState.item.id).toEqual(ITEM_ID)
    expect(itemUIState.item.content).toEqual(ITEM.content)
    expect(reduxActions.initItem).toHaveBeenCalled()
    expect(itemCtrl.itemContentForm).not.toBeNull()
    expect(itemCtrl.hasBody).toBeTruthy()

    expect(reduxActions.initEditSessions).toHaveBeenCalled()
    expect(reduxActions.setDiffMode).not.toHaveBeenCalled() // No diffWithVersion
})
