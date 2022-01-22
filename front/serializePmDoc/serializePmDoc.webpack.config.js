let webpack = require("webpack"),
    path = require('path');

const srcPath = path.resolve(__dirname, '../src');

module.exports = {
    entry: path.join(__dirname, 'serializePmDocES6.src.js'),
    output: {
        path: __dirname,
        filename: 'serializePmDocES6.js',
    },
    target: 'node',
    module: {
        rules: [
            {
                test: /\.vue$/,
                use: [
                    path.join(__dirname, 'emptyLoader.js')
                ],
            },
            {
                test: /\.js$/,
                loader: 'babel-loader'
            },
        ]
    },
    node: {
        console: true,
        global: true,
        process: true,
        Buffer: true,
        setImmediate: true
    },
    resolve: {
        extensions: ['.js', '.vue'],
        alias: {
            '@': srcPath,
            'pilot': srcPath,
            '@js': path.join(srcPath, 'js'),
            '@components': path.join(srcPath, 'components'),
            '@views': path.join(srcPath, 'views'),
            '@richText': path.join(srcPath, 'richText'),
            '@sass': path.join(srcPath, 'assets/sass'),
            '@svg': path.join(srcPath, 'assets/svg'),
            canvas: path.join(__dirname, 'canvas') // Needed because jsdom will try to import from 'canvas'
        },
        symlinks: false
    },
    performance: { hints: false },
}
