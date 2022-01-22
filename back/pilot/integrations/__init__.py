"""Pilot Public API

Disclaimer : there is no CSRF protection since this api is not supposed to be queried by an ajax client belonging
 to the same site.

This api allow consumer to retrieve articles belonging to cms-type channels and mark them as published.
There is no authentification. To use it you'll need to generate a channel token in the main user interface.

Each token is associated with a channel. Let's say tour token is : 7ba0d1874e3e8884ac197c27fa2aab03da4f706c

You'll need to change domain name and port number according to your installation.
The token will be passed as a custom header: channeltoken

All urls can be queried with or without trailing slash

Iot to retrieve the list of publication_ready articles associated to a channel (default list)

    curl   'http://127.0.0.1:8000/publicapi/v1/item/'  --header 'channeltoken:7ba0d1874e3e8884ac197c27fa2aab03da4f706c'

    Response:
  [
    {
        "id": 80,
        "title": "Item 80",
        "body": "Content 80",
        "state": "publication_ready",
        "publication_dt": "2014-11-03T22:59:59Z",
        "url": "/publicapi/v1/item/80/",
        "author": "@paolo"
    },
    ....
 ]

Appending state parameters (publication_ready, published, all)in a querystring allows to
query items according to their state

Querying the following url gives the same response (publication_ready articles )

    curl   'http://127.0.0.1:8000/publicapi/v1/item/?state=publication_ready'  --header 'channeltoken:...'

To retrieve the  list of published articles associated to a channel

    curl   'http://127.0.0.1:8000/publicapi/v1/item/?state=published'  --header 'channeltoken:...'

To retrieve the whole list of  articles associated to a channel

    curl   'http://127.0.0.1:8000/publicapi/v1/item/?state=all'  --header 'channeltoken:...'


To retrieve a specific article you have to append the item id.

    curl   'http://127.0.0.1:8000/publicapi/v1/item/80/'  --header 'channeltoken:...'

    Response:
    {
        "id": 80,
        "title": "Item 80",
        "body": "Content 80",
        "state": "publication_ready",
        "publication_dt": "2014-11-03T22:59:59Z",
        "url": "/publicapi/v1/item/80/",
        "author": "@paolo"
    }


To mark it as published, you have to make a HTTP PATCH request on its own url to update item state.
Parameters are: op:replace and state:published

    curl --request PATCH  'http://127.0.0.1:8000/publicapi/v1/item/80/'  --header 'channeltoken:...'
        --data "op=replace&state=published"

    Response:

    {
        "id": 80,
        "title": "Item 80",
        "body": "Content 80",
        "state": "published",
        "publication_dt": "2014-11-03T22:59:59Z",
        "url": "/publicapi/v1/item/80/",
        "author": "@paolo"
    }

Instead of using plain post-type data you can also send json

    curl --request PATCH  'http://127.0.0.1:8000/publicapi/v1/item/229/'  --header 'channeltoken:...'
        --header 'Content-type:application/json' --data '{"op":"replace", "state":"published"}'

Response: same as before

Obviously you can only mark publication_ready items. If you replay the last patch you'll get a HTTP 400 error and a
concise explanation

    {
        "error": "Item state does not allow modification."
    }

Sending invalid parameters will trigger a HTTP 400 errors and an explicit error message
    curl --request PATCH  'http://127.0.0.1:8000/publicapi/v1/item/229/'  --header 'channeltoken:...'
        --header 'Content-type:application/json' --data '{"op":"replace", "state":"published"}'

    {
        "error": "Invalid parameters"
    }
"""
