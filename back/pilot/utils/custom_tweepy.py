from tweepy.api import API
from tweepy.binder import bind_api


class CustomAPI(API):
    """ Tweepy api does not have yet this new twitter api (statuses/lookup )endpoint which returns fully-hydrated
    tweet objects for up to 100 tweets per request, as specified by comma-separated values passed to the id parameter.
    """

    status_lookup = bind_api(
        path='/statuses/lookup.json',
        method='POST',
        payload_type='status', payload_list=True,
        allowed_param=['id', 'include_entities ', 'trim_user ', 'map'],
        require_auth=True
    )
