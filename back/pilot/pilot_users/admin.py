from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from pilot.pilot_users.models import InvitationToken, PilotUser, Team, UserInDesk, UserInOrganization
from pilot.utils.api import csrf_protect_m, sensitive_post_parameters_m
from pilot.utils.url import get_fully_qualified_url
from pilot.pilot_users import admin_forms


class OrganizationsInline(admin.TabularInline):
    model = UserInOrganization
    fields = ('organization', 'is_organization_admin')
    raw_id_fields = ('organization',)
    extra = 1


class DesksInline(admin.TabularInline):
    model = UserInDesk
    fields = ('desk', 'permission')
    raw_id_fields = ('desk',)
    extra = 1


class OrphanUserListFilter(admin.SimpleListFilter):
    """
    Filter users which are desk-orphan :
    Neither active in a desk (have a UserInDesk M2M relation)
    nor inactive in a desk (have a UserInDeskDeactivated M2M relation)
    """
    title = _('Orphelin ( rattaché à aucun desk )')
    parameter_name = 'orphan'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Oui')),
            ('0', _('Non'))
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return (queryset
                    .filter(desks=None, desks_deactivated=None) # Orphan => not linked to a desk
                    .exclude(wiped=True) # Exclude wiped users, so we don't delete them by error
                    .exclude(id=1) # Exclude the user 1, so we don't delete it by error
                    .exclude(email='pilotbot@pilot.pm')) # Exclude the pilotbot user, so we don't delete it by error
        if self.value() == '0':
            return queryset.exclude(desks=None, desks_deactivated=None)
        return queryset


class PilotUserAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password', 'impersonate')}),
        (_('Informations personnelles'),{'fields': (
            'first_name',
            'last_name',
            'email',
            'language',
            'avatar',
            'phone',
            'localization',
            'job',
            'notification_preferences',
            'wiped'
        )}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser')}),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined', 'cgv_acceptance_date')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}),
    )

    list_display = ('username', 'impersonate', 'email', 'first_name', 'last_name', 'language', 'is_staff')

    list_filter = (OrphanUserListFilter, 'is_staff', 'is_superuser', 'desks',)

    ordering = ('username',)

    search_fields = ('username', 'first_name', 'last_name', 'email')

    actions = ['wipeout']

    form = admin_forms.PilotUserChangeForm
    add_form = admin_forms.PilotUserCreationForm
    add_form_template = 'admin/auth/user/add_form.html'
    change_password_form = AdminPasswordChangeForm
    change_user_password_template = None
    inlines = (OrganizationsInline, DesksInline,)
    readonly_fields = ('impersonate', )

    def impersonate(self, obj):
        url = get_fully_qualified_url('/impersonate/{}'.format(obj.pk))
        return mark_safe(f'<a href="{url}">Impersonate {obj.username}</a>')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(PilotUserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """Use special form during user creation."""
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': admin.utils.flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(PilotUserAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        from django.conf.urls import url
        return[
            url(r'^(\d+)/password/$', self.admin_site.admin_view(self.user_change_password))
        ] + super(PilotUserAdmin, self).get_urls()

    def lookup_allowed(self, lookup, value):
        # See #20078: we don't want to allow any lookups involving passwords.
        if lookup.startswith('password'):
            return False
        return super(PilotUserAdmin, self).lookup_allowed(lookup, value)

    @sensitive_post_parameters_m
    @csrf_protect_m
    def add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super(PilotUserAdmin, self).add_view(request, form_url, extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, pk, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = get_object_or_404(self.queryset(request), pk=pk)
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Changer le mot de passe de: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': '_popup' in request.GET or '_popup' in request.POST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        return TemplateResponse(
            request,
            self.change_user_password_template or 'admin/auth/user/change_password.html',
            context,
            current_app=self.admin_site.name
        )

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determines the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and '_popup' not in request.POST:
            request.POST['_continue'] = 1
        return super(PilotUserAdmin, self).response_add(request, obj, post_url_continue)

    def wipeout(self, request, queryset):
        try:
            with transaction.atomic():
                for user in queryset:
                    user.wipeout()
        except Exception as e:
            self.message_user(request, e, level=messages.ERROR)
    wipeout.short_description = "WIPEOUT user data"


admin.site.register(PilotUser, PilotUserAdmin)


class InvitationTokenAdmin(admin.ModelAdmin):
    list_display = ('email', 'permission', 'token', 'user', 'created_by', 'created_at', 'used_at', 'used')
    ordering = ('-created_at',)
    raw_id_fields = ('desk', 'user', 'created_by', 'updated_by')
    search_fields = ('email',)


admin.site.register(InvitationToken, InvitationTokenAdmin)

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',  'desk', 'description')
    ordering = ('name',)
    raw_id_fields = ('desk', 'created_by', 'updated_by')
    search_fields = ('name',)


admin.site.register(Team, TeamAdmin)
