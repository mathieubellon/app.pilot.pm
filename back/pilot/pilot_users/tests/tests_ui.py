from unittest import skip

from django.core import mail
from django.urls import reverse
from django.test import TestCase

from pilot.desks.tests import factories as desk_factories
from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.pilot_users.tests import invitations_factories
from pilot.utils import pilot_languages
from pilot.utils.test import PilotAdminUserMixin

@skip("Replaced by Vue.js interface")
class UsersUiInvitationsTest(PilotAdminUserMixin, TestCase):
    """Test user invitations."""

    def setUp(self):
        super(UsersUiInvitationsTest, self).setUp()
        # Keep a reference to the list view URL.
        self.users_list = reverse('ui_users_list')

    def test_invitation_token_segmentation(self):
        """Other desks and organizations invitations must not be visible.."""

        other_desk_other_org = desk_factories.DeskFactory()
        other_desk_same_org = desk_factories.DeskFactory(organization=self.organization)
        invit_otherdesk_same_org = invitations_factories.InvitationTokenFactory(desk=other_desk_same_org)
        invit_otherdesk_other_org = invitations_factories.InvitationTokenFactory(desk=other_desk_other_org)

        response = self.client.get(self.users_list)
        self.assertNotContains(response, invit_otherdesk_same_org.email)
        self.assertNotContains(response, invit_otherdesk_other_org.email)

    def test_invite_a_new_editor(self):
        """An admin invite a new editor. Test the full process."""

        url = reverse('ui_user_invite')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST, create a new user.
        post_data = {
            'permission': PERMISSION_EDITORS,
            'email': 'EDITOR@PILOT.COM',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.users_list)

        # An email containing an invitation token should have been sent to the new user.
        # Ensure that the email is in lower case (EmailLowerCaseField should be used in the Form).
        token = InvitationToken.objects.get(email=post_data['email'].lower())
        self.assertEqual(token.email, post_data['email'].lower())
        self.assertEqual(len(mail.outbox), 1)
        url = reverse(
            'ui_invitation_confirm',
            kwargs={'organization_pk': self.organization.pk, 'desk_pk': self.desk.pk, 'token': token.token}
        )
        self.assertIn(url, mail.outbox[0].body)

        # There should now be 1 pending invitation.
        response = self.client.get(self.users_list)
        self.assertEqual(len(response.context['pending_tokens']), 1)

        # Logout the admin.
        self.client.logout()

        # The new user clicked on the invitation link.
        url = reverse(
            'ui_invitation_confirm',
            kwargs={'organization_pk': self.organization.pk, 'desk_pk': self.desk.pk, 'token': token.token}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # The new user submitted the registration form.
        registration_post_data = {
            'first_name': 'Editor',
            'last_name': 'Editor',
            'password1': 'password',
            'password2': 'password',
            'username': 'EditorEditor',
        }
        response = self.client.post(url, data=registration_post_data)
        self.assertEqual(response.status_code, 302)

        # Test that the new user is automatically logged in.
        self.assertIn('_auth_user_id', self.client.session)
        self.client.logout()

        # Test that the new user can log in.
        user = PilotUser.objects.get(email=post_data['email'].lower())
        self.assertTrue(self.client.login(
            email=post_data['email'].lower(),
            password=registration_post_data['password1'])
        )
        self.client.logout()

        # Check new user permissions.
        self.assertFalse(user.permissions.is_admin)
        self.assertTrue(user.permissions.is_editor)
        self.assertFalse(user.permissions.is_restricted_editor)

    def test_confirm_lang(self):
        """Checking the lang switching"""

        url = reverse('ui_user_invite')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST, create a new user.
        post_data = {
            'permission': PERMISSION_EDITORS,
            'email': 'EDITOR@PILOT.COM',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.users_list)

        # An email containing an invitation token should have been sent to the new user.
        # Ensure that the email is in lower case (EmailLowerCaseField should be used in the Form).
        token = InvitationToken.objects.get(email=post_data['email'].lower())
        url = reverse(
            'ui_invitation_confirm',
            kwargs={
                'organization_pk': self.organization.pk,
                'desk_pk': self.desk.pk,
                'token': token.token
            }
        )

        # Logout the admin.
        self.client.logout()
        self.assertEqual(token.created_by.desks.all()[0].language, pilot_languages.FR_LANG)  # Sanity check
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lang="{0}"'.format(pilot_languages.FR_LANG))  # Check html lang
        self.assertEqual(response.context['LANGUAGE_CODE'], pilot_languages.FR_LANG)

        # Changing desk lang
        self.desk.language = pilot_languages.EN_LANG
        self.desk.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lang="{0}"'.format(pilot_languages.EN_LANG))  # Check html lang
        self.assertEqual(response.context['LANGUAGE_CODE'], pilot_languages.EN_LANG)

    def test_invite_a_new_admin(self):
        """An admin invite another new admin."""

        # Test POST, create a new user.
        url = reverse('ui_user_invite')
        post_data = {
            'permission': PERMISSION_ADMINS,
            'email': 'ADMIN@PILOT.COM',
        }
        response = self.client.post(url, data=post_data)

        # An email containing an invitation token should have been sent to the new user.
        # Ensure that the email is in lower case (EmailLowerCaseField should be used in the Form).
        token = InvitationToken.objects.get(email=post_data['email'].lower())
        self.assertEqual(token.email, post_data['email'].lower())

        # Logout the admin.
        self.client.logout()

        # The new user clicked on the invitation link.
        url = reverse(
            'ui_invitation_confirm',
            kwargs={'organization_pk': self.organization.pk, 'desk_pk': self.desk.pk, 'token': token.token}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # The new user submitted the registration form.
        registration_post_data = {
            'first_name': 'Admin',
            'last_name': 'Admin',
            'password1': 'password',
            'password2': 'password',
            'username': 'AdminAdmin',
        }
        response = self.client.post(url, data=registration_post_data)
        self.assertEqual(response.status_code, 302)

        # Check new user permissions.
        user = PilotUser.objects.get(email=post_data['email'].lower())
        self.assertTrue(user.permissions.is_admin)
        self.assertFalse(user.permissions.is_editor)
        self.assertFalse(user.permissions.is_restricted_editor)

    def test_invite_a_new_restricted_editor(self):
        """An admin invite a new restricted editor."""

        # Test POST, create a new user.
        url = reverse('ui_user_invite')
        post_data = {
            'permission': PERMISSION_RESTRICTED_EDITORS,
            'email': 'RESTRICTED.EDITOR@PILOT.COM',
        }
        response = self.client.post(url, data=post_data)

        # An email containing an invitation token should have been sent to the new user.
        # Ensure that the email is in lower case (EmailLowerCaseField should be used in the Form).
        token = InvitationToken.objects.get(email=post_data['email'].lower())
        self.assertEqual(token.email, post_data['email'].lower())

        # Logout the admin.
        self.client.logout()

        # The new user clicked on the invitation link.
        url = reverse(
            'ui_invitation_confirm',
            kwargs={'organization_pk': self.organization.pk, 'desk_pk': self.desk.pk, 'token': token.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # The new user submitted the registration form.
        registration_post_data = {
            'first_name': 'Restricted',
            'last_name': 'Editor',
            'password1': 'password',
            'password2': 'password',
            'username': 'RestrictedEditor',
        }
        response = self.client.post(url, data=registration_post_data)
        self.assertEqual(response.status_code, 302)

        # Check new user permissions.
        user = PilotUser.objects.get(email=post_data['email'].lower())
        self.assertFalse(user.permissions.is_admin)
        self.assertFalse(user.permissions.is_editor)
        self.assertTrue(user.permissions.is_restricted_editor)

    def test_delete_invitation(self):
        invitation = invitations_factories.InvitationTokenFactory.create(organization=self.organization, desk=self.desk)
        invitation_other_desk_same_org = invitations_factories.InvitationTokenFactory.create(
            organization=self.organization
        )
        invitation_other_desk_other_org = invitations_factories.InvitationTokenFactory.create()
        self.assertEqual(3, InvitationToken.objects.all().count())

        # Test GET.
        url = reverse('ui_invitation_delete', kwargs={'token': invitation.token, })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST, delete the invitation.
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(2, InvitationToken.objects.all().count())

        # Test GET and POST segmentation
        for invit in (invitation_other_desk_same_org, invitation_other_desk_other_org):
            url = reverse('ui_invitation_delete', kwargs={'token': invit.token, })
            get_response = self.client.get(url)
            post_response = self.client.post(url)
            # Invitations from other desks and organizations cannot be deleted
            self.assertEqual(get_response.status_code, 404)
            self.assertEqual(post_response.status_code, 404)


@skip("Replaced by Vue.js interface")
class UsersUiEditTest(PilotAdminUserMixin, TestCase):
    """Test user edition."""

    def test_user_edit(self):
        new_user = pilot_users_factories.EditorFactory.create()
        new_user.organizations.add(self.organization)
        new_user.desks.add(self.desk)

        url = reverse('ui_user_edit', kwargs={'user_pk': new_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(new_user.is_active)
        self.assertTrue(new_user.permissions.is_editor)

        post_data = {
            'permission': PERMISSION_RESTRICTED_EDITORS,
            'is_active': False,
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_users_list'))

        # Refresh the cached new_user instance.
        new_user = PilotUser.objects.get(pk=new_user.pk)

        self.assertFalse(new_user.is_active)
        self.assertFalse(new_user.permissions.is_editor)
        self.assertTrue(new_user.permissions.is_restricted_editor)
