import os

from unittest import skip

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pilot.utils.selenium_test import SeleniumTest

@skip('Skip test create item in modal')
class ItemAddFunctionnalTests(SeleniumTest):

    def setUp(self):
        super(ItemAddFunctionnalTests, self).setUp()
        self.login_user()


    def test_add_simple_item(self):
        self.display_list_items()
        self.select_add_item('Classique')
        my_item = {'title': 'My title'}
        self.create_item(my_item)
        self.items_list_contains(my_item)

    def test_add_twitter_item(self):
        self.display_list_items()
        self.select_add_item('Tweet')
        my_item = {
            'title': 'My title',
            'publication_date': '01/01/2015',
            'publication_time': '12:00'
        }
        self.create_item(my_item)
        self.items_list_contains(my_item)

    def test_display_backend_errors(self):
        self.display_list_items()
        self.select_add_item('Classique')
        my_item = {
            'title': 'My title',
            'publication_dt': '01/01/1200'
        }
        self.create_item(my_item)
        self.check_display_error("l'année doit être supérieure à 1900")

    def login_user(self):
        self.browser.get('%s%s' % (self.live_server_url, '/'))
        self.wait.until(lambda driver: driver.find_element_by_tag_name('body'))
        username_input = self.browser.find_element_by_name('username')
        username_input.send_keys(self.user.email)
        password_input = self.browser.find_element_by_name('password')
        password_input.send_keys('password')
        self.browser.find_element_by_tag_name('button').click()
        self.assertIn('Tableau de bord', self.browser.title)
        payload_text = self.browser.find_element_by_id('app-body').text
        self.assertIn("responsable d'aucun projet", payload_text)

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
        dialog_text = self.browser.find_element_by_css_selector('.ngdialog.add-item').text
        self.assertIn("Ajouter un contenu de type %s" % content_type, dialog_text)

    def create_item(self, item_params):
        for key,value in item_params.items():
            input_title = self.browser.find_element_by_id("id_%s" % key)
            input_title.send_keys(value)
        submit_button = self.browser.find_element_by_css_selector('.add-item .button.submit')
        submit_button.click()

    def items_list_contains(self, item):
         WebDriverWait(self.browser, 10).until(
             EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.list-contents'), item['title'])
         )

    def check_display_error(self, message):
        error_message = self.browser.find_element_by_css_selector('.ngdialog .text-error:not(.ng-hide)').text
        self.assertIn(message, error_message)
