import re
import unicodedata

from django.db import transaction
from django.utils import timezone, translation

from pilot.accounts.models import SubscriptionPlan
from pilot.desks.models import Desk
from pilot.notifications import emailing
from pilot.organizations.models import Organization
from pilot.pilot_users.models import PERMISSION_ADMINS, PilotUser, UserInDesk, UserInOrganization
from pilot.utils import pilot_languages


def derivate_username(email):
    base_username = email.split('@')[0]
    base_username = unicodedata.normalize('NFKD', base_username).encode('ascii', 'ignore').decode('ascii')
    base_username = base_username.replace('.', '_')
    base_username = base_username.replace('-', '_')
    base_username = re.sub(r'\s', '_', base_username)
    base_username = re.sub(r'[^\w_]', '', base_username)
    base_username = base_username.strip()

    i = 1
    username = base_username
    while PilotUser.objects.filter(username__iexact=username).exists():
        username = f"{base_username}{i}"
        i += 1
    return username


def create_new_desk(request, data):
    """Create a new user of the system with admin privileges."""
    with transaction.atomic():
        organization_name = data['organization']

        # email will always be lower-cased, so will be the username
        email = data['email']
        username = derivate_username(email)

        # For new users, associate the language they chose on the signin UI.
        user_language = pilot_languages.validate_user_language(request.session.get(translation.LANGUAGE_SESSION_KEY))

        # 1) Create user.
        new_user = PilotUser.objects.create_user(
            username=username,
            password=data['password1'],
            email=email,
            language=user_language,
            cgv_acceptance_date=timezone.now()
        )

        # 2) Create organization.
        organization = Organization.objects.create(
            name=organization_name,
            billing_name=organization_name,
            created_by=new_user,
            is_active=False # Make sure that the new organization is NOT active until email confirmation.
        )

        # 3) Create the first desk.
        desk = Desk.objects.create(
            name=organization_name,  # Keep the organization's name.
            created_by=new_user,
            organization=organization,
            subscription_plan=SubscriptionPlan.get_trial_subscription(),
            is_active=False # Make sure that the new desk is NOT active until email confirmation.
        )

        # 4) Add the new user to the organization with admin permission
        UserInOrganization.objects.create(
            user=new_user,
            organization=organization,
            is_organization_admin=True
        )

        # 5) Add the new user to the desk with admin permission
        UserInDesk.objects.create(
            user=new_user,
            desk=desk,
            permission=PERMISSION_ADMINS
        )

        # 5) Ask for email confirmation.
        emailing.send_email_confirmation(new_user)


def activate_new_desk(user):
    """Activate the desk and organization of the user which has confirmed his email"""
    desk = user.desks.first()
    desk.is_active = True
    desk.save()
    desk.organization.is_active = True
    desk.organization.save()


def associate_invited_user_to_desk(user, token):
    """Associate an user to a desk after an invitation link has been confirmed."""
    with transaction.atomic():
        desk = token.desk

        # 1) Add the new user to the organization, if he's not already a part of it
        if not UserInOrganization.objects.filter(user=user, organization=desk.organization).exists():
            UserInOrganization.objects.create(
                user=user,
                organization=desk.organization,
                is_organization_admin=False
            )

        # 2) Add the new user to the desk.
        UserInDesk.objects.create(
            user=user,
            desk=desk,
            permission=token.permission
        )

        # 3) Copy its teams
        for team in token.teams.all():
            user.teams.add(team)

        # 4) Create the relation between the new user and the token and mark the token as used.
        token.user = user
        token.used = True
        token.used_at = timezone.now()
        token.save()

        return user


def create_invited_user(request, data, token):
    """Creates a new user after an invitation link has been confirmed."""
    with transaction.atomic():
        # For new users, associate the language they chose on the signin UI.
        user_language = pilot_languages.validate_user_language(request.session.get(translation.LANGUAGE_SESSION_KEY))

        # 1) Create user.
        new_user = PilotUser.objects.create_user(
            username=derivate_username(token.email),
            password=data['password1'],
            email=token.email,
            cgv_acceptance_date=timezone.now(),
            language=user_language
        )

        # 2) Associate it to the desk
        return associate_invited_user_to_desk(new_user, token)
