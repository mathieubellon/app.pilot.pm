// great resource in addition to the webpack/babel doc :
// https://dev.to/pixelgoo/how-to-configure-webpack-from-scratch-for-a-basic-website-46a5

let path = require("path"),
    webpack = require("webpack"),
    BundleTracker = require("webpack-bundle-tracker"),
    MiniCssExtractPlugin = require("mini-css-extract-plugin"),
    { CleanWebpackPlugin } = require("clean-webpack-plugin"),
    TerserPlugin = require("terser-webpack-plugin"),
    VueLoaderPlugin = require("vue-loader/lib/plugin")

const srcPath = path.resolve(__dirname, "src"),
    devServerHost = process.env.LAN_IP ? process.env.LAN_IP : "localhost",
    devServerPort = "3000"

module.exports = function getConfig(env, argv) {
    env = env ? env : {}
    let optimization = {}
    let devServer = {}
    let outputFilename
    let styleLoader
    let stats = {
        children: false,
        colors: true,
        modules: false,
    }

    let plugins = [
        new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
        new VueLoaderPlugin(),
        new BundleTracker({
            path: __dirname,
            filename: env.prod ? "./webpack-stats.json" : "./webpack-stats-dev.json",
            indent: true,
        }),
    ]

    // prod env
    if (env.prod) {
        // In production, we add a hash on the file
        // We use [chunkhash] so the hash is changed only if the content has changed.
        // This will help with browser caching.
        outputFilename = "[name].[chunkhash].js"
        plugins = [
            ...plugins,
            new CleanWebpackPlugin({ verbose: true }),
            new MiniCssExtractPlugin({
                // [contenthash] is a special hash for the extracted content
                filename: "[name].[contenthash].css",
                chunkFilename: "[id].css",
            }),
        ]
        optimization = {
            minimizer: [new TerserPlugin({ sourceMap: true })],
        }
        //  In production, we use MiniCssExtract to extract the generated css from the js bundle,
        // and output it in a separate file.
        styleLoader = {
            loader: MiniCssExtractPlugin.loader,
            options: {
                hmr: false,
            },
        }
    }
    // dev env
    else {
        // In development, we don't use hash on the file name ( faster and morannotationLayere clear )
        outputFilename = "[name].js"
        plugins = [...plugins, new webpack.HotModuleReplacementPlugin()]
        // Disable some optimization to gain performance in dev
        optimization = {
            removeAvailableModules: false,
            removeEmptyChunks: false,
            splitChunks: false,
        }

        // In development, we use style-loader to enable HMR on style with the dev-server
        styleLoader = "style-loader"

        devServer = {
            host: devServerHost,
            port: devServerPort,
            headers: { "Access-Control-Allow-Origin": "*" },
            publicPath: `http://${devServerHost}:${devServerPort}/static/`,
            inline: true,
            overlay: true,
            hot: true,
            stats,
        }
    }

    return {
        mode: env.prod ? "production" : "development",
        entry: {
            main: [
                // Plyr need custom-event-polyfill and url-polyfill
                "custom-event-polyfill",
                "url-polyfill",
                path.resolve("./src/index"), // entry point of the main app
            ],
            anonymous: [
                // Plyr need custom-event-polyfill and url-polyfill
                "custom-event-polyfill",
                "url-polyfill",
                path.resolve("./src/indexPublic"), // entry point of the public app
            ],
            "pdf.worker": "pdfjs-dist/build/pdf.worker.entry",
        },
        output: {
            path: path.resolve("./public/"),
            publicPath: env.prod ? "/static/" : `http://${devServerHost}:${devServerPort}/static/`,
            filename: (chunkData) => {
                return chunkData.chunk.name === "pdf.worker" ? "pdf.worker.js" : outputFilename
            },
        },
        module: {
            rules: [
                {
                    test: /\.vue$/,
                    include: srcPath,
                    use: ["cache-loader", "vue-loader"],
                },
                {
                    test: /\.js$/,
                    include: srcPath,
                    use: {
                        loader: "babel-loader",
                        options: {
                            cacheDirectory: true,
                        },
                    },
                },
                {
                    test: /\.(scss|css)$/,
                    // The following loaders are applied in reverse order :
                    use: [
                        // 4/ In production, we use MiniCssExtract to extract the generated css from the js bundle,
                        // and output it in a separate file.
                        // In development, we use style-loader to enable HMR on style
                        styleLoader,
                        // 3/ Resolves url() and @imports inside CSS
                        "css-loader",
                        // 2/ We apply PostCSS transformations ( @apply from tailwindcss, minification, autoprefixer)
                        "postcss-loader",
                        // 1/ We transform SASS to standard CSS
                        {
                            loader: "sass-loader",
                            options: {
                                // Prefer `dart-sass`
                                implementation: require("sass"),
                            },
                        },
                    ],
                },
                {
                    test: /\.(png|jpg|gif|ico)$/,
                    loader: "file-loader",
                    options: {
                        name: "[name].[ext]?[hash]",
                    },
                },
                {
                    test: /\.svg$/,
                    // svg-loader v0.12 add an object rest spread operator,
                    // which needs to be transpiled by babel by using the babel-loader.
                    // See https://github.com/visualfanatic/vue-svg-loader/issues/63
                    use: [
                        {
                            loader: "babel-loader",
                            options: {
                                cacheDirectory: true,
                            },
                        },
                        {
                            loader: "vue-svg-loader",
                            options: {
                                svgo: {
                                    plugins: [
                                        { removeDimensions: false },
                                        { removeViewBox: false },
                                    ],
                                },
                            },
                        },
                    ],
                },
            ],
        },
        resolve: {
            extensions: [".js", ".scss", ".json", ".vue"],
            modules: ["node_modules", srcPath],
            alias: {
                "@": srcPath,
                pilot: srcPath,
                "@js": path.join(srcPath, "js"),
                "@components": path.join(srcPath, "components"),
                "@views": path.join(srcPath, "views"),
                "@richText": path.join(srcPath, "richText"),
                "@sass": path.join(srcPath, "assets/sass"),
                "@svg": path.join(srcPath, "assets/svg"),
            },
            symlinks: false,
        },
        devtool: env.prod ? `source-map` : "none", // 'eval-source-map' can be useful for debugging on dev
        // Remove the following warnings  :
        // WARNING in entrypoint size limit
        // WARNING in asset size limit
        performance: { hints: false },
        plugins,
        optimization,
        stats,
        devServer,
    }
}
