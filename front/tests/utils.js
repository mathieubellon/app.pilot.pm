const { spawn, execFileSync } = require("child_process")
const url = require("url")
const pg = require("pg")
const fs = require("fs")

const DEBUG = false

/***********************
 * Database connection
 ************************/

let databaseUrl

if (process.env.DATABASE_URL) {
    databaseUrl = process.env.DATABASE_URL
} else {
    let privateSettings = fs.readFileSync("pilot/settings/_private_settings.py", "utf8")
    let matches = privateSettings.match(/DATABASE_URL\s*=.*["'](.*)["'].*$/m)

    if (matches) {
        databaseUrl = matches[1]
    } else {
        databaseUrl = "postgres://localhost:5432/pilotprod"
    }
}

const dbParams = url.parse(databaseUrl)
let dbAuth
if (dbParams.auth) {
    dbAuth = dbParams.auth.split(":")
} else {
    dbAuth = [null, null]
}

let pgConfig = {
    user: dbAuth[0],
    password: dbAuth[1],
    host: dbParams.hostname,
    port: dbParams.port,
    database: "test_" + dbParams.pathname.split("/")[1],
}
let pgPool = new pg.Pool(pgConfig)

/***********************
 * Django Test Server
 ************************/

const serverHost = "localhost"
const serverPort = "8001"
const serverBaseUrl = serverHost + ":" + serverPort

// The django test server
let testServer

let noServer = process.argv.indexOf("--noserver") > -1

let serverReadyPromise = new Promise(function (resolve, reject) {
    if (noServer) {
        resolve()
        return
    }

    // Prevent the server to buffer the startup messages
    process.env["PYTHONUNBUFFERED"] = 1

    testServer = spawn("python", [
        "manage.py",
        "nightwatch_test_server",
        "--addrport",
        serverBaseUrl,
        "--settings=pilot.settings.tests",
        "--noinput",
        "--keepdb",
    ])

    testServer.stdout.on("data", (data) => {
        if (DEBUG) console.log(`stdout: ${data}`)

        // Server is now running, we can resolve the promise
        if (data.includes("Quit the server with")) {
            resolve()
        }
    })

    if (DEBUG) {
        testServer.stderr.on("data", (data) => {
            console.log(`stderr: ${data}`)
        })
    }
})

if (DEBUG) {
    testServer.on("close", (code) => {
        console.log(`child process exited with code ${code}`)
    })
}

function stopTestServer() {
    if (testServer) {
        testServer.kill("SIGTERM")
    }
}

class TestServerOutput {
    startCapture() {
        this.captured = ""
        this.captureListener = (data) => {
            this.captured += data
        }
        testServer.stdout.on("data", this.captureListener)
    }
    stopCapture() {
        testServer.stdout.removeListener("data", this.captureListener)
    }
    getCapturedOutput() {
        return this.captured
    }
}
let testServerOutput = new TestServerOutput()

/***********************
 * Fixtures
 ************************/

/**
 * // Reset the test database between each nightwatch test
 */
function resetTestDatabase(fixtureName = null) {
    let args = ["manage.py", "reset_test_database", "--settings=pilot.settings.tests"]
    if (fixtureName) {
        args.push(fixtureName)
    }
    execFileSync("python", args)
}

/***********************
 * Nightwatch.js helpers
 ************************/

function getFullUrl(url) {
    return "http://" + serverBaseUrl + url
}
function login(browser) {
    browser
        .url(getFullUrl("/"))
        .setValue("#id_username", "john.doe1@example.com")
        .setValue("#id_password", "password")
        .click('button[type="submit"]')
        .pause(200)
}
function setupNightwatchTest(browser, fixtureName = null) {
    resetTestDatabase(fixtureName)
    browser.maximizeWindow()
    login(browser)
}

export {
    pgPool,
    serverReadyPromise,
    stopTestServer,
    testServerOutput,
    resetTestDatabase,
    getFullUrl,
    login,
    setupNightwatchTest,
}
