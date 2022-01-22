/**
 * Need the transpiled pmjtmdES6.js file
 * ( see serializePmDocES6.src.js for instructions )
 */
require('./serializePmDocES6.js')
let fs = require('fs')

let argument = process.argv[2]
let transferMode = process.argv[3]
let outputFormat = process.argv[4]

let source = ''
if(transferMode === 'tempfile'){
    source = fs.readFileSync(argument)
}else if(transferMode === 'argument'){
    source = argument
}
else{
    throw Exception("Incorrect transfer mode " + transferMode)
}

if( !source ){
    process.exit(1)
}

let jsonDocument = JSON.parse(source)

let output
if(outputFormat === 'html'){
    output = global.prosemirrorJsonToHTML(jsonDocument)
}else if(outputFormat === 'markdown'){
    output = global.prosemirrorJsonToMarkdown(jsonDocument)
}
else if(outputFormat === 'text'){
    output = global.prosemirrorJsonToText(jsonDocument)
}
else{
    throw Exception("Incorrect output format " + outputFormat)
}

process.stdout.write(output)

process.exit(0)
