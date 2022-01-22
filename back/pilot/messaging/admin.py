from django import forms
from django.contrib import admin
from django.db.models import Count, Q

from pilot.messaging.models import Message
from pilot.pilot_users.models import PERMISSION_ADMINS, PilotUser


class BaseMessageAdminForm(forms.ModelForm):
    content_fr = forms.CharField(
        widget=forms.Textarea
    )
    content_en = forms.CharField(
        widget=forms.Textarea
    )

    class Meta:
        model = Message
        fields = (
            'name',
            'type',
            'content_fr',
            'content_en',
        )
        
    def __init__(self, *args, **kwargs):
        super(BaseMessageAdminForm, self).__init__(*args, **kwargs)
        self.initial['content_fr'] = self.instance.content.get('fr')
        self.initial['content_en'] = self.instance.content.get('en')

    def save(self, commit=True):
        instance = super(BaseMessageAdminForm, self).save(commit)
        instance.content = {
            'fr': self.cleaned_data['content_fr'],
            'en': self.cleaned_data['content_en'],
        }
        return instance


class CreateMessageAdminForm(BaseMessageAdminForm):
    send_to_all_users = forms.BooleanField(required=False)
    send_to_all_admins = forms.BooleanField(required=False)

    class Meta:
        model = Message
        fields = (
            'send_to_all_users',
            'send_to_all_admins'
        ) + BaseMessageAdminForm.Meta.fields


class EditMessageAdminForm(BaseMessageAdminForm):
    pass


class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'recipient_count', 'read_count', 'unread_count')
    list_filter = ( 'type',)
    search_fields = ('name',)
    readonly_fields = ('recipient_count', 'read_count', 'unread_count', 'created_by', 'created_at', 'readers')

    def get_queryset(self, request):
        """
        Queryset annotated with counters
        """
        return super(MessageAdmin, self).get_queryset(request).annotate(
            recipient_count=Count('user_message_set'),
            read_count=Count('user_message_set', filter=Q(user_message_set__read_at__isnull=False)),
            unread_count=Count('user_message_set', filter=Q(user_message_set__read_at__isnull=True)),
        )

    def recipient_count(self, message):
        return message.recipient_count

    def read_count(self, message):
        return message.read_count

    def unread_count(self, message):
        return message.unread_count

    def readers(self, message):
        results = message.users.filter(user_message_set__read_at__isnull=False).values_list('username')
        list_result = [entry for entry in results]
        return list_result

    def get_form(self, request, obj=None, change=False, **kwargs):
        return EditMessageAdminForm if change else CreateMessageAdminForm

    def _get_form_for_get_fields(self, request, obj):
        return self.get_form(request, obj, change=bool(obj), fields=None)

    def save_model(self, request, message, form, change):
        """
        Given a model instance save it to the database.
        """
        if not change:
            message.created_by = request.user

        message.save()

        if not change:
            if form.cleaned_data.get('send_to_all_users'):
                message.send(
                    PilotUser.objects.all()
                )

            elif form.cleaned_data.get('send_to_all_admins'):
                message.send(
                    PilotUser.objects.filter(
                        user_in_desk_set__permission=PERMISSION_ADMINS
                    ).distinct()
                )


admin.site.register(Message, MessageAdmin)
