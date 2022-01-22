import copy

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from django.urls import reverse

from pilot.utils.test import prosemirror_body, EMPTY_PROSEMIRROR_DOC
from pilot.utils.selenium_test import SeleniumTest

from pilot.items.tests import factories as items_factories
from pilot.item_types import initial_item_types
from pilot.item_types.tests.testing_item_type_definition import ADVANCED_TEST_SCHEMA, VALIDATION_TEST_SCHEMA
from pilot.item_types.tests import factories as item_types_factories

from pilot.utils.prosemirror.prosemirror import prosemirror_json_to_text


class SeleniumItemFormTest(SeleniumTest):

    def send_params(self, item_params):
        for key,value in item_params.items():
            if key == 'body':
                self.set_prosemirror_content(value)
            else:
                current_input = self.browser.find_element_by_id("id_%s" % key)
                current_input.send_keys(value)
        submit_button = self.browser.find_element_by_css_selector('.panel-add-item .button.submit')

        submit_button.click()


    def create_custom_item(self, item_type):
        self.item_type = item_types_factories.ItemTypeFactory.create(
            desk=self.desk,
            content_schema=copy.deepcopy(item_type)
        )
        self.new_item_type = self.item_type.technical_name
        self.item = items_factories.ItemFactory.create(
            desk=self.desk,
            item_type=self.item_type,
            json_content={
                'char': 'abc',
                'integer': 1
            }
        )

class SeleniumItemAddUiTest(SeleniumItemFormTest):
    """Test C on Item objects."""

    def setUp(self):
        super(SeleniumItemAddUiTest, self).setUp()
        self.login_user()

    def test_display_form_from_list(self):
        item_type = item_types_factories.ItemTypeFactory.create(desk=self.desk, name='MyName')
        for [display_name, technical_name] in [
                ['Classique', 'default'],
                ['Tweet', 'twitter'],
                ['Statut Facebook', 'facebook'],
                ['MyName', item_type.technical_name]
                ]:
            self.display_list_items()
            self.select_add_item(display_name)
            expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_add_with_item_type', kwargs={'item_type': technical_name}))
            self.assertEqual(expected_url, self.browser.current_url)

    def test_add_default_item(self):
        self.display_add_form('Classique', 'default')
        self.send_params({'title': u'Mÿ tîtlé'})
        item = Item.objects.last()
        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)
        self.assertEqual(u'Mÿ tîtlé', item.title)

    def test_error_tweet(self):
        self.display_add_form('Tweet', 'twitter')
        self.send_params({'title': u'Mÿ tîtlé', 'body': u'Mÿ Côñtênt'})
        for css_selector in ['.publication-date-error', '.publication-time-error']:
            text_error = self.browser.find_element_by_css_selector(css_selector).text
            self.assertIn('Ce champ est obligatoire.', text_error)
        self.send_params({'title': u'àdd', 'body': u'àdd', 'publication_date': '01/01/2015', 'publication_time': '10:30'})
        item = Item.objects.last()
        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)
        self.assertEqual(u'Mÿ tîtléàdd', item.title)
        self.assertEqual(prosemirror_body(u'àddMÿ Côñtênt'), item.content['body'])

    def test_error_tweet_body_not_update(self):
        self.display_add_form('Tweet', 'twitter')
        self.send_params({'title': u'Mÿ tîtlé', 'body': u'Mÿ Côñtênt'})
        for css_selector in ['.publication-date-error', '.publication-time-error']:
            text_error = self.browser.find_element_by_css_selector(css_selector).text
            self.assertIn('Ce champ est obligatoire.', text_error)
        self.send_params({'title': u'àdd', 'publication_date': '01/01/2015', 'publication_time': '10:30'})
        item = Item.objects.last()
        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)
        self.assertEqual(u'Mÿ tîtléàdd', item.title)
        self.assertEqual(prosemirror_body(u'Mÿ Côñtênt'), item.content['body'])

    def test_remaining_char_in_tweet_body(self):
        self.display_add_form('Tweet', 'twitter')
        self.set_prosemirror_content('0')
        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.remaining-char-widget'), '139')
        )

    def test_remaining_char_in_title(self):
        content_schema = copy.deepcopy(ADVANCED_TEST_SCHEMA)
        item_type = item_types_factories.ItemTypeFactory.create(
            desk=self.desk,
            name='MyName',
            content_schema=content_schema
        )
        self.display_add_form('MyName', item_type.technical_name)
        title_input = self.browser.find_element_by_id("id_title")
        title_input.send_keys('t')
        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.remaining-char-widget'), '69')
        )

    def display_add_form(self, content_type, technical_name):
        self.browser.get('%s%s' % (self.live_server_url, reverse('ui_item_add_with_item_type', kwargs={'item_type': technical_name})))
        dialog_text = self.browser.find_element_by_id('app-body').text
        self.assertIn("Ajouter un contenu de type %s" % content_type, dialog_text)

    def display_list_items(self):
        self.browser.get('%s%s' % (self.live_server_url, '/items/list/'))
        self.assertIn('Contenus', self.browser.title)

    def select_add_item(self, content_type):
        add_button = self.browser.find_element_by_css_selector('.add-item')
        add_button.click()
        self.wait.until(lambda driver: driver.find_element_by_css_selector('.menu.visible'))
        menu = add_button.find_element_by_css_selector('.menu.visible')
        link_content_type = self.browser.find_element_by_link_text(content_type)
        link_content_type.click()
        dialog_text = self.browser.find_element_by_id('app-body').text
        self.assertIn("Ajouter un contenu de type %s" % content_type, dialog_text)

class SeleniumItemCopyUiTest(SeleniumItemFormTest):
    """Test copy on Item objects."""

    def setUp(self):
        super(SeleniumItemCopyUiTest, self).setUp()
        self.login_user()

    def test_copy_with_showed_body(self):
        self.item = items_factories.ItemTweetFactory.create(desk=self.desk)
        self.new_item_type = initial_item_types.TWITTER_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))

        body = prosemirror_json_to_text(self.item.body)
        initial_value =  '{}'.format(280-len(body))

        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR,'.remaining-char-widget'), initial_value),
            'number {} not found in page'.format(initial_value)
        )
        submit_button = self.browser.find_element_by_css_selector('.panel-add-item .button.submit')
        submit_button.click()

        copy_item = Item.objects.latest('created_at')
        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': copy_item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)
        self.assertEqual(self.item.content['body'], copy_item.content['body'])
        self.assertEqual(self.item.content['title'], copy_item.content['title'])

    def test_copy_with_hidden_body(self):
        self.item = items_factories.ItemTweetFactory.create(desk=self.desk)
        self.new_item_type = initial_item_types.FACEBOOK_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))

        submit_button = self.browser.find_element_by_css_selector('.panel-add-item .button.submit')
        submit_button.click()

        copy_item = Item.objects.latest('created_at')
        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': copy_item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)
        self.assertEqual(self.item.content['body'], copy_item.content['body'])
        self.assertEqual(self.item.content['title'], copy_item.content['title'])

    def test_copy_with_content(self):
        self.create_custom_item(VALIDATION_TEST_SCHEMA)
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))

        submit_button = self.browser.find_element_by_css_selector('.panel-add-item .button.submit')
        submit_button.click()
        self.assertEqual(2, Item.objects.count())
        item = Item.objects.latest('created_at')

        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)
        self.assertEqual(u'abc', item.content['char'])
        self.assertEqual(1, item.content['integer'])

    def test_remaining_char_in_title(self):
        self.create_custom_item(ADVANCED_TEST_SCHEMA)
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))

        title_input = self.browser.find_element_by_id("id_title")
        title_input.send_keys('t')
        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.remaining-char-widget'), '69')
        )

    def test_remaining_char_in_tweet_body(self):
        self.item = items_factories.ItemFactory.create(desk=self.desk)
        self.new_item_type = initial_item_types.TWITTER_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))

        body = prosemirror_json_to_text(self.item.body)
        initial_value =  '{}'.format(280-len(body))

        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR,'.remaining-char-widget'), initial_value),
            'number {} not found in page'.format(initial_value)
        )

        self.set_prosemirror_content('0')
        new_value =  '{}'.format(139-len(body))
        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR,'.remaining-char-widget'), new_value),
            'number {} not found in page'.format(new_value)
        )

    def test_error_tweet(self):
        self.item = items_factories.ItemFactory.create(desk=self.desk)
        self.new_item_type = initial_item_types.TWITTER_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))

        self.browser.find_element_by_id('id_publication_date').clear()
        submit_button = self.browser.find_element_by_css_selector('.panel-add-item .button.submit')
        submit_button.click()

        for css_selector in ['.publication-date-error', '.publication-time-error']:
            text_error = self.browser.find_element_by_css_selector(css_selector).text
            self.assertIn('Ce champ est obligatoire.', text_error)
        self.send_params({'title': u'àdd', 'body': u'àdd', 'publication_date': '01/01/2015', 'publication_time': '10:30'})
        new_item = Item.objects.latest('created_at')
        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': new_item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)
        self.assertEqual(u'{}àdd'.format(self.item.title), new_item.title)
        initial_text_body = prosemirror_json_to_text(self.item.body)
        self.assertEqual(prosemirror_body(u'àdd{}'.format(initial_text_body)), new_item.content['body'])

    def test_copy_tags(self):
        self.item = items_factories.ItemFactory.create(desk=self.desk)
        self.item.tags.add('foo')
        self.item.tags.add('bar')
        self.new_item_type = initial_item_types.ARTICLE_TYPE

        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))

        submit_button = self.browser.find_element_by_css_selector('.panel-add-item .button.submit')
        submit_button.click()

        copy_item = Item.objects.latest('created_at')
        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': copy_item.pk}))

        self.assertEqual(2, copy_item.tags.all().count())
        for expected_tag in ['foo', 'bar']:
             self.assertTrue(expected_tag in map(lambda t: t.name, copy_item.tags.all()), '{} is not found'.format(expected_tag))



class SeleniumItemModifyUiTest(SeleniumItemFormTest):
    """Test modify on Item objects."""

    def setUp(self):
        super(SeleniumItemModifyUiTest, self).setUp()
        self.login_user()

    def test_with_showed_body(self):
        self.item = items_factories.ItemFactory.create(desk=self.desk)
        initial_item_content = {'title': self.item.content['title'],
                         'body': self.item.content['body']}
        self.new_item_type = initial_item_types.TWITTER_TYPE
        url = reverse('ui_item_types_edit', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))

        body = prosemirror_json_to_text(self.item.body)
        initial_value =  '{}'.format(280-len(body))

        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR,'.remaining-char-widget'), initial_value),
            'number {} not found in page'.format(initial_value)
        )

        self.send_params({'publication_time': '10:30'})

        self.assertEqual(1, Item.objects.count())
        modified_item = Item.objects.latest('created_at')

        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': self.item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)
        self.assertEqual(initial_item_content['body'], modified_item.content['body'])
        self.assertEqual(initial_item_content['title'], modified_item.content['title'])

    def test_with_hidden_body(self):
        self.item = items_factories.ItemFactory.create(desk=self.desk)
        initial_item_content = {'title': self.item.content['title'],
                                'body': self.item.content['body']}
        self.new_item_type = initial_item_types.FACEBOOK_TYPE
        url = reverse('ui_item_types_edit', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))
        submit_button = self.browser.find_element_by_css_selector('.panel-add-item .button.submit')
        submit_button.click()

        self.send_params({'publication_time': '10:30'})
        self.assertEqual(1, Item.objects.count())
        modified_item = Item.objects.latest('created_at')

        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': self.item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)
        self.assertEqual(initial_item_content['body'], modified_item.content['body'])
        self.assertEqual(initial_item_content['title'], modified_item.content['title'])

    def test_error_tweet(self):
        self.item = items_factories.ItemFactory.create(desk=self.desk)
        initial_item_content = {'title': self.item.content['title'],
                                'body': prosemirror_json_to_text(self.item.body)}
        self.new_item_type = initial_item_types.TWITTER_TYPE
        url = reverse('ui_item_types_edit', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))

        self.browser.find_element_by_id('id_publication_date').clear()
        submit_button = self.browser.find_element_by_css_selector('.panel-add-item .button.submit')
        submit_button.click()

        for css_selector in ['.publication-date-error', '.publication-time-error']:
            text_error = self.browser.find_element_by_css_selector(css_selector).text
            self.assertIn('Ce champ est obligatoire.', text_error)
        self.send_params({'title': u'àdd', 'body': u'àdd', 'publication_date': '01/01/2015', 'publication_time': '10:30'})

        self.assertEqual(1, Item.objects.count())
        modified_item = Item.objects.latest('created_at')

        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': self.item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)
        self.assertEqual(u'{}àdd'.format(initial_item_content['title']), modified_item.title)
        self.assertEqual(prosemirror_body(u'àdd{}'.format(initial_item_content['body'])), modified_item.content['body'])

    def test_modify_to_type_with_required_field(self):
        self.item = items_factories.ItemFactory.create(desk=self.desk)
        initial_item_content = {'title': self.item.content['title'],
                         'body': self.item.content['body']}

        item_type = item_types_factories.ItemTypeFactory.create(
            desk=self.desk,
            content_schema=copy.deepcopy(VALIDATION_TEST_SCHEMA)
        )
        self.new_item_type = item_type.technical_name
        url = reverse('ui_item_types_edit', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})
        self.browser.get('%s%s' % (self.live_server_url, url))

        submit_button = self.browser.find_element_by_css_selector('.panel-add-item .button.submit')
        submit_button.click()

        self.assertEqual(1, Item.objects.count())
        modified_item = Item.objects.latest('created_at')

        expected_url = '%s%s' % (self.live_server_url, reverse('ui_item_details', kwargs={'item_pk': self.item.pk}))
        self.assertEqual(expected_url, self.browser.current_url)

    def test_clean_content(self):
        self.create_custom_item(VALIDATION_TEST_SCHEMA)
        self.new_item_type = initial_item_types.ARTICLE_TYPE
        url = reverse('ui_item_types_edit', kwargs={'item_pk': self.item.pk, 'new_item_type': self.new_item_type})

        self.browser.get('%s%s' % (self.live_server_url, url))

        submit_button = self.browser.find_element_by_css_selector('.panel-add-item .button.submit')
        submit_button.click()


        self.assertEqual(1, Item.objects.count())
        modified_item = Item.objects.latest('created_at')

        self.assertEqual(u'', modified_item.content['title'])
        self.assertEqual(EMPTY_PROSEMIRROR_DOC, modified_item.content['body'])
        self.assertTrue('char' not in modified_item.content)
        self.assertTrue('integer' not in modified_item.content)
