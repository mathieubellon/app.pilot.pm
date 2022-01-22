/***********************
 * Fake resource
 ************************/

const USER = {
    id: 1,
    username: "Chuck Norris",
    avatar: null,
}

/***********************
 * Mocking
 ************************/

let annotationManager, $httpBackend

beforeEach(inject(function (_$httpBackend_, AnnotationsManager) {
    $httpBackend = _$httpBackend_
    $httpBackend.whenGET("/api/users/me/").respond(USER)
    annotationManager = new AnnotationsManager()
}))

mockCommonRequests()

afterEach(function () {
    $httpBackend.verifyNoOutstandingExpectation()
    $httpBackend.verifyNoOutstandingRequest()
})

/***********************
 * Tests
 ************************/

test.skip("exists", () => {
    $httpBackend.flush()

    expect(annotationManager).toBeDefined()
    expect(annotationManager.annotations).toEqual({})
    expect(annotationManager.pmView).toBeNull()
    expect(annotationManager.currentUser).toBeDefined()
    expect(annotationManager.selectedAnnotations).toEqual([])
    expect(annotationManager.currentComment).toEqual("")
    expect(annotationManager.editedComment).toBeNull()
    expect(annotationManager.confirmDeletionAnnotation).toBeNull()
    expect(annotationManager.annotationInCreation).toBeNull()
    expect(annotationManager.dirty).toBeFalsy()
})

test.skip("pick user data", () => {
    let userWithJunk = _.clone(USER)
    userWithJunk.junk = "junk"
    $httpBackend.expectGET("/api/users/me/").respond(userWithJunk)
    $httpBackend.flush()

    // Junk has been discarded
    expect(annotationManager.currentUser).toEqual(USER)
})
