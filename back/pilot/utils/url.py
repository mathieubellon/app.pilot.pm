from django.conf import settings


def get_fully_qualified_url(absolute_url):
    """
    Return a fully qualified url into the application, from an absolute url,
    taking into account the http protocol and the FQDN.

    Exemple:
    "/items/2/" ==> "https://app.pilot.pm/items/2/"
    """
    return "{}://{}{}".format(
        settings.HTTP_PROTOCOL,
        settings.FQDN,
        absolute_url
    )


def get_server_name():
    return settings.FQDN.split(':')[0]