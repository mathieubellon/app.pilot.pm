import Vue from "vue"

import UserList from "../admin/UserList"
import UserStore from "../admin/UsersAdminStore"
import UserRouter from "../admin/_router"

/***********************
 * Fake resource
 ************************/

const nbUser = 10
let USERS = []
for (let i = 0; i < nbUser; i++) {
    USERS.push({
        id: i,
        username: "user " + i,
    })
}

/***********************
 * Tests
 ************************/

test.skip("display users", (done) => {
    const vm = getTestingVueInstance(UserList, UserStore, UserRouter)
    vm.$store.commit("setActivesUsers", USERS)

    Vue.nextTick().then(() => {
        expect(vm.$el.querySelectorAll(".user-list__element").length).toEqual(nbUser)
        done()
    })
})
