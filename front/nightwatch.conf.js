require("babel-register")()

const glob = require("glob")

let srcFolders = glob.sync("tests/**/__functionaltests__")

module.exports = {
    src_folders: srcFolders,
    globals_path: "tests/nightwatch.init.js",
    custom_assertions_path: "tests/nightwatch_assertions",
    custom_commands_path: "tests/nightwatch_commands",

    selenium: {
        start_process: false,
    },

    test_settings: {
        default: {
            globals: {
                waitForConditionTimeout: 1000,
                waitForConditionPollInterval: 100,
            },
            selenium_port: 9515,
            selenium_host: "localhost",
            default_path_prefix: "",

            desiredCapabilities: {
                browserName: "chrome",
                chromeOptions: {
                    args: [
                        "--headless",
                        "--no-sandbox",
                        "--disable-gpu", // This is for windows
                    ],
                },
                javascriptEnabled: true,
                acceptSslCerts: true,
            },

            screenshots: {
                enabled: true,
                path: "./tests_output/screenshots/",
                on_failure: true,
            },
        },

        debug: {
            desiredCapabilities: {
                chromeOptions: {
                    args: ["--no-sandbox"],
                },
            },
        },
    },
}
