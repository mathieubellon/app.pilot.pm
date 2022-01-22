import os
import signal
import time
from unittest import skip

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils.translation import activate
from django.test import override_settings
from django.conf import settings

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.phantomjs.webdriver import WebDriver as PhantomDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pilot.utils.test import PilotAdminUserMixin, MediaMixin

class SeleniumDriver:
    Chrome = 'Chrome'
    Phantom = 'Phantom'

@skip("Skip selenium")
@override_settings(MEDIA_ROOT=MediaMixin.TEST_MEDIA_ROOT)
class SeleniumTest(PilotAdminUserMixin, StaticLiveServerTestCase):
    driver = SeleniumDriver.Chrome

    @classmethod
    def init_browser(cls):
        if cls.driver == SeleniumDriver.Phantom:
            cls.browser = PhantomDriver()
            cls.browser.implicitly_wait(3)
            cls.browser.set_window_size(1400, 1000)

        elif cls.driver == SeleniumDriver.Chrome:
            cls.browser = ChromeDriver()
            cls.browser.implicitly_wait(3)
            cls.browser.maximize_window()

    @classmethod
    def exit_browser(cls):
        if cls.driver == SeleniumDriver.Phantom:
            cls.browser.service.process.send_signal(signal.SIGTERM)

        cls.browser.quit()

    @classmethod
    def setUpClass(cls):
        super(SeleniumTest, cls).setUpClass()
        #cls.init_browser()

    @classmethod
    def tearDownClass(cls):
        #cls.exit_browser()
        super(SeleniumTest, cls).tearDownClass()

    def setUp(self):
        super(SeleniumTest, self).setUp()
        #self.fail()
        self.wait = WebDriverWait(self.browser, 3)
        activate('FR-fr')

    def tearDown(self):
        filename = "%s_%s" % (self.__class__.__name__,self._testMethodName)
        directory = os.path.join(settings.MEDIA_ROOT, 'phantomjs')
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.browser.save_screenshot(os.path.join(directory, "%s.png" % filename))
        with open(os.path.join(directory, "%s.html" % filename), "w") as html_file:
            html_file.write(self.browser.page_source.encode('utf-8'))
        super(SeleniumTest, self).tearDown()

    def get_fqdn_url(self, url):
        return '{}{}'.format(self.live_server_url, url)

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

    def wait_for_prosemirror(self):
        prosemirror = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, "prosemirror"))
        )
        return prosemirror.find_element_by_class_name("ProseMirror")

    def set_prosemirror_content(self, content):
        prosemirror_content = self.wait_for_prosemirror()
        # We cannot send the keys right away when the class is visible,
        # We need to wait a little so angular is correctly inited.
        time.sleep(0.5)
        # Selenium with phantomJS doesn't know how to handle contenteditable
        # See : https://github.com/seleniumhq/selenium-google-code-issue-archive/issues/8076
        # And : https://github.com/detro/ghostdriver/issues/401
        #
        # But clicking on the contenteditable first seems to fix the issue
        if self.driver == SeleniumDriver.Phantom:
            prosemirror_content.click()
        prosemirror_content.send_keys(content)

        return prosemirror_content
