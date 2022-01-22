# Asset logic flow 

Asset upload/update/convert/ workflow is pretty complex with 3 tiers to handle (app, S3, transloadit.com, ..)
So Let's write down ths flow story

The first step is mandatory. If a user display/preview a 10M image its ok.
Hard coupling uploading and preview calculation is hard and prone to instability.
So our strategy is uploading original file first and mandatory (even if user display a 10M image as a preview, it's slow but it's possible)
Previewing is optionnal and under "best effort, fail fast and fall back to original file" strategy.


##1 Uploading


User select file to upload (either create or update)
Dropzone ask for infos from our API (/s3_signature endpoint, response is file key, s3 signature, version, metadata,..) then upload to S3 with those informations
DropZone.vue Ligne 264

Upload original to s3 with setting or updating a version number
File version info is in metadata on s3, not in file key (to keep file url consistency across channels)
Preview with original url
Depending on file extension choose a reader for preview and/or icon for display


Where to trigger conversion :  from front on asset display ? from back on create / update methods ?


#2 Previewing

If file can have cover:
    If conversion.version == asset.version and asset.conversion not none:

        if conversion is completed:
            Display cover

        else if conversion is running
            trigger check conversion only because conversion is only triggered by backend
            if detail view:
                Display original if possible  + Display 'preview is calculating' animated GIF
            if listview :
                return icon depending on file extension + animation "preview calculating"
            when checkconveersion status is completed replace original by cover
                

        else if conversion is error
            display message
            if detail view:
                return Display original if possible if in detail view
            if list view
                return icon depending on file extension if in list view
    else
        trigger check conversion only because conversion is only triggered by backend
        if detail view:
            return Display original if in detail view
        if list view
            return icon depending on file extension if in list view
        when checkconveersion status end replace original by cover
           return cover

Else
    # ex. zip file cannot have cover
    return icon depending on file extension


AssetDetail.vue, listen for Dropzone fileUploadSuccess event to trigger conversion with transloadit (POST/conversion endpoint)
Can be manually triggered

When conversion order is successfull we trigger a periodical check for  conversion status (GET/checkconversionstatus endpoint)
Can be manually triggered

On production (and not on dev) Transloadit can callback us when assembly is completed (either errored or successfull, /conversioncompleted endpoint)
We must find or ensure a system to stop callbacking / checking status when assembly is complete





