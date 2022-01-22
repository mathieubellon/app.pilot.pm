const chromedriver = require("chromedriver")
import { serverReadyPromise, stopTestServer, pgPool } from "./utils"

module.exports = {
    before: (done) => {
        chromedriver.start()
        serverReadyPromise.then(done)
    },

    after: (done) => {
        chromedriver.stop()
        pgPool.end()
        stopTestServer()
        done()
    },
}
