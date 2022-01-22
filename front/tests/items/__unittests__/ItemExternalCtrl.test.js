import { getProsemirrorContent } from "./fixtures/prosemirror"

/***********************
 * Fake resource
 ************************/

const ITEM_ID = 1
const REVIEW_ID = 1
const REVIEW_TOKEN = "abc"
const REVIEW = {
    id: REVIEW_ID,
    content: {
        title: "Title",
        body: getProsemirrorContent("meh"),
    },
    is_editable: false,
}

/***********************
 * Controller mocking
 ************************/

// See https://docs.angularjs.org/guide/unit-testing
let itemExternalCtrl, $httpBackend, $scope, itemUIState

beforeEach(inject(function (_$httpBackend_, $rootScope, $controller) {
    // Mock Review ressource
    $httpBackend = _$httpBackend_

    // Testing scope
    $scope = $rootScope.$new()

    // Mock item State
    itemUIState = {}

    // Instanciate the test controller
    itemExternalCtrl = $controller("ItemExternalCtrl", {
        $scope: $scope,
        itemUIState: itemUIState,
    })
}))

mockCommonRequests()

afterEach(function () {
    $httpBackend.verifyNoOutstandingExpectation()
    $httpBackend.verifyNoOutstandingRequest()
})

function initReview() {
    $httpBackend.expectGET("/api/items/1/reviews/1/abc/").respond(REVIEW)
    itemExternalCtrl.setItemSharing(ITEM_ID, REVIEW_ID, REVIEW_TOKEN)
    $httpBackend.flush()
}

/***********************
 * Tests
 ************************/

test.skip("exists", () => {
    expect(itemExternalCtrl).toBeDefined()
    expect(itemExternalCtrl.itemReview).toBeNull()
    expect(itemExternalCtrl.itemContentForm).toBeNull()
    expect(itemExternalCtrl.thankyou).toBeFalsy()
    expect(itemExternalCtrl.displayAssets).toBeFalsy()

    expect($scope.noAnnotations).toBeTruthy()
    expect($scope.itemReady).toBeFalsy()
    expect($scope.itemUIState).toBe(itemUIState)

    // Just to validate verifyNoOutstandingRequest
    $httpBackend.flush()
})

test.skip("init review", () => {
    initReview()
    expect(itemExternalCtrl.itemReview.id).toEqual(REVIEW_ID)
    expect(itemUIState.itemReadOnly.content).toEqual(REVIEW.content)
    expect(itemUIState.editable).toEqual(REVIEW.is_editable)
    expect(itemExternalCtrl.itemContentForm).not.toBeNull()
    expect($scope.itemReady).toBeTruthy()
})
