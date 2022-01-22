import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from ipware.ip import get_ip


@receiver(user_logged_in)
def sig_user_logged_in(sender, user, request, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info("user logged in: %s at %s" % (user, get_ip(request)))


@receiver(user_logged_out)
def sig_user_logged_out(sender, user, request, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info("user logged out: %s at %s" % (user, get_ip(request)))


@receiver(user_login_failed)
def sig_user_login_failed(sender, credentials, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info("user login failed: %s" % (credentials))
