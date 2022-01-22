from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.contrib.postgres import fields as pg_fields


class TwitterCredentialsManager(models.Manager):
    def get_queryset(self):
        return super(TwitterCredentialsManager, self).get_queryset().exclude(
            access_token_key='',
            access_token_secret=''
        )

    def for_desk(self, desk):
        return self.get_queryset().filter(channel__desk=desk)


class TwitterCredential(models.Model):
    CHECK_TIMEDELTA = timedelta(0, 1200, 0)
    twitter_account = models.CharField(max_length=100)

    channel = models.OneToOneField(
        Channel,
        verbose_name=_("Canal"),
        on_delete=models.CASCADE
    )
    access_token_key = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255)

    validity = models.BooleanField(default=False)
    last_time_checked = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    valid = TwitterCredentialsManager()

    def __str__(self):
        return self.twitter_account

    def is_not_empty(self):
        return not self.access_token_key.isspace() and not self.access_token_secret.isspace()

    def check_validity(self, save=True):
        """ Check the validity of the credential and stores the validity if save is True.
        """
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)

        auth.set_access_token(self.access_token_key, self.access_token_secret)

        api = tweepy.API(auth)

        try:
            api_is_valid = bool(api.verify_credentials())
        except Exception:
            api_is_valid = False

        self.validity = api_is_valid
        self.last_time_checked = timezone.now()
        if save:
            self.save()
        return bool(api_is_valid)

    def is_valid(self):
        """ Check the validity of the credential if last update is older than CHECK_TIMEDELTA and returns the validity.
        """
        delta = timedelta.max

        if self.last_time_checked:
            delta = timezone.now() - self.last_time_checked

        if delta > self.CHECK_TIMEDELTA:
            self.check_validity(save=False)
        return self.validity

    def save(self, *args, **kwargs):
        self.check_validity(save=False)
        super(TwitterCredential, self).save(*args, **kwargs)


class FacebookCredentialsManager(models.Manager):
    def get_queryset(self):
        return super(FacebookCredentialsManager, self).get_queryset().exclude(
            access_token='', validity=False, page_publishing_permission=False
        )

    def for_desk(self, desk):
        return self.get_queryset().filter(channel__desk=desk)


class FacebookCredential(models.Model):
    """ This model holds the connection data related to facebook.
    The connection can be either used to publish on a page or a user timeline.
    """
    USER_TYPE = 0
    PAGE_TYPE = 1
    FACEBOOK_TYPE_CHOICES = (
        (USER_TYPE, _('Timeline utilisateur')),
        (PAGE_TYPE, _('Page'))
    )

    facebook_account = models.CharField(max_length=100)
    CHECK_TIMEDELTA = timedelta(days=1)

    channel = models.OneToOneField(
        Channel,
        verbose_name=_("Canal"),
        on_delete=models.CASCADE
    )
    facebook_type = models.PositiveSmallIntegerField(choices=FACEBOOK_TYPE_CHOICES, default=USER_TYPE)
    access_token = models.CharField(max_length=512)
    facebook_id = models.CharField(max_length=255, null=True, blank=True)
    facebook_page_name = models.CharField(max_length=255, null=True, blank=True)
    facebook_page_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    facebook_page_token = models.CharField(max_length=512, null=True, blank=True)

    validity = models.BooleanField(default=False)
    page_publishing_permission = models.BooleanField(default=False)
    last_time_checked = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    valid = FacebookCredentialsManager()

    def __str__(self):
        return self.facebook_account

    @property
    def is_for_user(self):
        return self.facebook_type == self.USER_TYPE

    @property
    def is_for_page(self):
        return self.facebook_type == self.PAGE_TYPE

    def get_relevant_id(self):
        if self.is_for_user:
            return self.facebook_id
        return self.facebook_page_id

    def get_relevant_token(self):
        if self.is_for_user:
            return self.access_token
        return self.facebook_page_token

    def get_relevant_name(self):
        if self.is_for_user:
            return self.facebook_account
        return self.facebook_page_name

    # Social features disabled for now
    # def check_validity(self, save=True):
    #     """ Checks the validity of the credential and stores the validity if save is True.
    #     """
    #     graph = facebook.GraphAPI(self.access_token)
    #     try:
    #         api_is_valid = bool(graph.get_object("me"))
    #     except facebook.GraphAPIError:
    #         api_is_valid = False
    #         self.page_publishing_permission = False
    #
    #     self.validity = api_is_valid
    #     if save:
    #         self.last_time_checked = timezone.now()
    #         self.save()
    #     return bool(api_is_valid)

    # Social features disabled for now
    # def check_publish_permissions(self, save=True):
    #     """ Checks that we can publish on facebook user stream and store the result.
    #     """
    #     graph = facebook.GraphAPI(self.access_token)
    #     can_publish_on_page = False
    #     try:
    #         permissions = graph.get_object("me/permissions", path='permissions')
    #         can_manage_pages = any(['manage_pages' in perm.values() for perm in permissions['data']])
    #         can_publish_stream = any(['publish_actions' in perm.values() for perm in permissions['data']])
    #     except facebook.GraphAPIError:
    #         self.page_publishing_permission = False
    #         can_manage_pages = False
    #         can_publish_stream = False
    #
    #     graph = facebook.GraphAPI(self.facebook_page_token)
    #     try:
    #         page_permissions = graph.get_object("me/admins")
    #         for user in page_permissions['data']:
    #             if self.facebook_id == user.get('id') and 'CREATE_CONTENT' in user.get('perms'):
    #                 can_publish_on_page = True
    #     except facebook.GraphAPIError:
    #         can_publish_on_page = False
    #
    #     if self.facebook_type == self.PAGE_TYPE:
    #         self.page_publishing_permission = can_manage_pages and can_publish_on_page and can_publish_stream
    #     else:
    #         self.page_publishing_permission = can_publish_stream
    #     if save:
    #         self.last_time_checked = timezone.now()
    #         self.save()
    #     return self.page_publishing_permission

    def is_valid(self):
        """ Check the validity of the credential if last update is older than CHECK_TIMEDELTA and returns the validity.
        """
        delta = timedelta.max

        if self.last_time_checked:
            delta = timezone.now() - self.last_time_checked

        if delta > self.CHECK_TIMEDELTA:
            self.check_validity(save=False)
        return self.validity

    def can_publish(self):
        """ Check the validity of the credential if last update is older than CHECK_TIMEDELTA and returns the validity.
        """
        delta = timedelta.max

        if self.last_time_checked:
            delta = timezone.now() - self.last_time_checked

        if delta > self.CHECK_TIMEDELTA:
            self.check_publish_permissions(save=False)

        return self.page_publishing_permission


class TweetLog(models.Model):
    """ Holds logs about tweets """

    PUBLISHED_STATUS = 0
    ERROR_STATUS = 1
    STATUS_CHOICES = (
        (PUBLISHED_STATUS, _("Publié")),
        (ERROR_STATUS, _("Erreur"))
    )
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE,)
    tweet_id = models.CharField(max_length=20)
    text = models.CharField(max_length=280)
    tweet_dt = models.DateTimeField(default=timezone.now)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PUBLISHED_STATUS)

    info = pg_fields.JSONField(null=True, blank=True)
    last_checked = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Tweet Log")
        verbose_name_plural = _("Tweet Logs")
        ordering = ['-tweet_dt']

    def __str__(self):
        return self.tweet_id


class FacebookLog(models.Model):
    """ Holds logs about tweets """

    PUBLISHED_STATUS = 0
    ERROR_STATUS = 1
    STATUS_CHOICES = (
        (PUBLISHED_STATUS, _("Publié")),
        (ERROR_STATUS, _("Erreur"))
    )
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE,)
    status_id = models.CharField(max_length=128)
    text = models.TextField()
    status_dt = models.DateTimeField(default=timezone.now)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PUBLISHED_STATUS)

    info = pg_fields.JSONField(null=True, blank=True)
    last_checked = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Facebook Log")
        verbose_name_plural = _("Facebook Logs")
        ordering = ['-status_dt']

    def __str__(self):
        return self.status_id
