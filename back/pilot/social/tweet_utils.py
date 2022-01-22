import ast

from django.conf import settings
from django.utils import timezone
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

# from twitter_text import TwitterText
# from twitter_text.regex import REGEXEN


# class TwitterMaxLengthValidator(object):
#     message = _('Contenu trop long. Twitter autorise seulement %(limit_value)d signes '
#                 '( %(show_value)d signes saisis)')
#     code = 'twitter_max_length'
#     limit_value = settings.TWITTER_MAX_LENGTH
#
#     def __call__(self, value):
#         tt = get_body_input_as_text(value)
#         t = TwitterText(tt)
#         length = t.validation.tweet_length()
#         if length > self.limit_value:
#             params = {'limit_value': self.limit_value, 'show_value': length}
#             raise ValidationError(self.message, code=self.code, params=params)


# class TwitterInvalidValidator(object):
#     message = _('Tweet invalide')
#     code = 'twitter_invalid'
#     allow_empty = True
#
#     def __call__(self, value):
#         """
#         Check the text for any reason that it may not be valid as a Tweet. This is meant as a pre-validation
#         before posting to api.twitter.com. There are several server-side reasons for Tweets to fail but this pre-validation
#         will allow quicker feedback.
#
#         Returns false if this text is valid. Otherwise one of the following Symbols will be returned:
#
#             "Empty text":: if the text is empty
#             "Invalid characters":: if the text contains non-Unicode or any of the disallowed Unicode characters
#         """
#         tt = get_body_input_as_text(value)
#         t = TwitterText(tt)
#
#         valid = True # optimism
#         validation_error = None
#
#         # Empty text is considered invalid for publication to tweeter,
#         # but accepted by pilot during content editing
#         if not self.allow_empty and not t.validation.tweet_length():
#             valid, validation_error = False, _('Texte vide')
#
#         if re.search(r''.join(REGEXEN['invalid_control_characters']), t.text):
#             valid, validation_error = False, _('Caractères invalides')
#
#         if not valid:
#             raise ValidationError(validation_error, code=self.code)


def post_on_twitter(twitter_item, check_publication_dt=True, user=None):
    """ Try to update a status on twitter. """
    from pilot.social.models import TweetLog

    api_is_valid = False
    log_status = TweetLog.ERROR_STATUS
    tweet_id = 'none'
    text = _("Erreur indéfinie")
    status = False
    error = None

    try:
        credentials = twitter_item.channel.twittercredential
    except AttributeError:
        return False, [{'message': _("Le canal associé ne dispose pas des droits de publication nécessaires.")}]

    if check_publication_dt:
        if twitter_item.publication_dt > timezone.now():
            return False, [{'message': _("La date de publication est dans le futur")}]

    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)

    auth.set_access_token(credentials.access_token_key, credentials.access_token_secret)

    api = tweepy.API(auth)

    try:
        api_is_valid = api.verify_credentials()
    except Exception as error:
        text = str(error)

    if api_is_valid:
        try:
            status = api.update_status(twitter_item.body)
        except tweepy.TweepError as error:
            tweet_id = 'none'
            text = smart_str(error)
        if status:
            twitter_item.publish(user=user)
            tweet_id = status.id
            text = status.text
            log_status = TweetLog.PUBLISHED_STATUS

    twitter_item.tweetlog_set.all().delete()
    TweetLog.objects.create(
        item=twitter_item,
        tweet_id=tweet_id,
        text=text,
        status=log_status
    )
    if error:
        # The Tweepy api returns single quoted chars so we need a trick
        # we use python ast module to evaluate the string as a data structure before dumping
        # it with json module. The ast.literal_eval() method is said to be safe and does not evaluate
        # malicious code but data structures.
        # This code id also present in core.social.management.commands.publish_tweets.py and should be DRYed.
        try:
            error = ast.literal_eval(error.reason.strip())
        except Exception:
            error = [{'message': _("Erreur indéfinie")}]
    return status, error
