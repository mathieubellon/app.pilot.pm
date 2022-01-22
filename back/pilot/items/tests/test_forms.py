from django import forms
from django.test import TestCase

from pilot.pilot_users.tests import factories as user_factories
from pilot.utils.test import PilotAdminUserMixin

# TODO : migrate tests in this file

# class ItemContentFormFieldsTest(PilotAdminUserMixin, TestCase):
#     def setUp(self):
#         super(ItemContentFormFieldsTest, self).setUp()
#
#         self.content_schema = [
#             {
#                 'name': 'integer',
#                 'field': 'django.forms.IntegerField',
#                 'field_kwargs': {
#                     'label': 'test label',
#                     'help_text': 'test help text'
#                 },
#                 'serializer': 'rest_framework.serializers.IntegerField',
#             },
#             {
#                 'name': 'float',
#                 'field': 'django.forms.FloatField',
#                 'field_kwargs': {},
#                 'serializer': 'rest_framework.serializers.FloatField',
#             },
#             {
#                 'name': 'char',
#                 'field': 'django.forms.CharField',
#                 'field_kwargs': {},
#                 'serializer': 'rest_framework.serializers.CharField',
#             },
#         ]
#
#     def test_form_fields(self):
#         form = ItemContentForm(content_schema=self.content_schema)
#         field_names = form.fields.keys()
#         self.assertItemsEqual(field_names, ['integer', 'float', 'char'])
#
#     def test_form_field_types(self):
#         form = ItemContentForm(content_schema=self.content_schema)
#         fields = form.fields
#
#         self.assertIsInstance(fields['integer'], forms.IntegerField)
#         self.assertIsInstance(fields['float'], forms.FloatField)
#         self.assertIsInstance(fields['char'], forms.CharField)
#
#     def test_field_kwargs(self):
#         form = ItemContentForm(content_schema=self.content_schema)
#         field = form.fields['integer']
#         self.assertEqual(field.label, 'test label')
#         self.assertEqual(field.help_text, 'test help text')
#
#
# class ItemContentFormWidgetsTest(PilotAdminUserMixin, TestCase):
#     def setUp(self):
#         super(ItemContentFormWidgetsTest, self).setUp()
#
#         self.content_schema = [
#             {
#                 'name': 'radio_input',
#                 'field': 'django.forms.ChoiceField',
#                 'field_kwargs': {
#                     'required': True,
#                     'choices': (
#                         ('aa', 'Choice A'),
#                         ('bb', 'Choice B'),
#                     )
#                 },
#                 'widget': 'django.forms.RadioSelect',
#                 'widget_kwargs': {
#                     'attrs': {'class': 'radio-select-class'}
#                 },
#                 'serializer': 'rest_framework.serializers.CharField',
#             }
#         ]
#
#     def test_field_kwargs(self):
#         form = ItemContentForm(content_schema=self.content_schema)
#         field = form.fields['radio_input']
#
#         self.assertIsInstance(field.widget, forms.RadioSelect)
#         self.assertEqual(field.widget.attrs, {'class': 'radio-select-class'})
#
#
# class FormTest(PilotAdminUserMixin, TestCase):
#     def test_form(self):
#         """Testing that AddItemForm only show active desk users."""
#         self.users = user_factories.PilotUserFactory.create_batch(3)
#         self.inactive_users = user_factories.PilotUserFactory.create_batch(4, is_active=False)
#         self.other_desk_users = user_factories.PilotUserFactory.create_batch(6)
#         self.desk.users.add(*self.users)
#         self.desk.users.add(*self.inactive_users)
#         form = AddItemForm(desk=self.desk)
#
#         # Despite the users created we only get active desk users in the owners field
#         expected_user_count = self.desk.users.filter(is_active=True).count()
#         self.assertEqual(form.fields['owners'].queryset.count(), expected_user_count)
