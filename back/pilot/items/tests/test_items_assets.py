import time

from unittest import skip

from django.urls import reverse

from pilot.assets.tests import factories as assets_factories
from pilot.items.tests import factories as items_factories

from pilot.utils.selenium_test import SeleniumTest


@skip('Functional test pour item assets')
class ItemsAssetsJsTest(SeleniumTest):
    """Testing assets dynamic methods."""

    def setUp(self):
        super(ItemsAssetsJsTest, self).setUp()
        self.assets = [
            assets_factories.JpegAssetFactory(desk=self.desk),
            assets_factories.TxtAssetFactory(desk=self.desk),
        ]
        self.item = items_factories.ItemFactory.create(
            desk=self.desk,
            assets=self.assets,
            json_content={}
            )
        self.login_user()

    def test_embed_image_asset(self):
        """ Testing that the embed button works."""

        url = reverse('ui_item_details', kwargs={'item_pk': self.item.pk})
        self.browser.get('%s%s' % (self.live_server_url, url))


        time.sleep(1)
        self.browser.find_element_by_css_selector('#tab-assets-link a').click()
        WebDriverWait(self.browser, 1)

        time.sleep(1)
        button = WebDriverWait(self.browser, 1).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                'li#tab-assets button.embedasset[data-type=image]'
            ))
        )

        button.click()

        url = button.get_attribute('data-url')
        title = button.get_attribute('data-title')
        link = '![{}]({})'.format(title, url)

        content = self.browser.find_element_by_id("id_body")
        self.assertEqual(content.get_attribute('value'), link)

    def test_embed_non_image_asset(self):
        """ Testing that the embed button works."""

        url = reverse('ui_item_details', kwargs={'item_pk': self.item.pk})
        self.browser.get('%s%s' % (self.live_server_url, url))

        content = self.browser.find_element_by_id("id_body")
        self.assertEqual(content.get_attribute('value'), '')

        self.browser.find_element_by_css_selector('#tab-assets-link a').click()
        WebDriverWait(self.browser, 1)
        button = self.browser.find_element_by_css_selector('li#tab-assets button.embedasset[data-type=file]')
        time.sleep(5)
        button.click()

        url = button.get_attribute('data-url')
        title = button.get_attribute('data-title')
        link = '[{}]({})'.format(title, url)

        content = self.browser.find_element_by_id("id_body")
        self.assertEqual(content.get_attribute('value'), link)
