import { pgPool } from "../utils"

/**
 * Execute an SQL query on the database, and send the response to the callback
 */
export function command(sqlQuery, callback) {
    this.perform((done) => {
        pgPool
            .query(sqlQuery)
            .then((pgResponse) => {
                callback(pgResponse, done)
            })
            .catch((error) => {
                console.error(error)
                done()
            })
    })
}
