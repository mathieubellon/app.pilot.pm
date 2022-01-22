from datetime import datetime, timedelta

from django.urls import reverse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains


from pilot.utils.selenium_test import SeleniumTest

from pilot.projects.tests import factories as projects_factories
from pilot.channels.tests import factories as channels_factories
from pilot.items.tests import factories as items_factories
from pilot.pilot_users.tests import factories as user_factories
from pilot.targets.tests import factories as targets_factories

class SeleniumItemsCalendarTest(SeleniumTest):

    def setUp(self):
        super(SeleniumItemsCalendarTest, self).setUp()
        self.today = datetime.today()
        self.login_user()

    def check_content_label(self, expected_label):
        content = self.browser.find_element_by_css_selector('.popover-content').text
        #item has no title the title text is empty, we have
        content_label = filter(lambda line: ' :' in line, content.split('\n'))
        self.assertEqual(expected_label, content_label)

    def display_calendar(self, title):
        url = reverse('ui_main_calendar')
        self.browser.get('%s%s' % (self.live_server_url, url))

        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.calendar'), title)
        )

    def display_tooltip(self, title):
        self.check_nb_item_in_calendar(1, title)
        #there is only one item in calendar the following selector work
        item_display = self.browser.find_element_by_css_selector('.fc-content')
        actions = ActionChains(self.browser)
        actions.move_to_element(item_display)
        actions.perform()
        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.popover-title'), title)
        )

    def check_nb_item_in_calendar(self, number, title):
        calendar_text = self.browser.find_element_by_css_selector('.calendar').text
        self.assertEqual(number, calendar_text.count(title))

    def test_several_items(self):
        items = []
        for day in range(2):
            items.append(items_factories.ItemFactory.create(
                desk=self.desk,
                publication_dt=datetime(self.today.year, self.today.month, day+1)))
        url = reverse('ui_main_calendar')
        self.browser.get('%s%s' % (self.live_server_url, url))

        self.display_calendar(items[0].title)
        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.calendar'), items[1].title)
        )

    def test_tooltip(self):
        item = items_factories.ItemFactory.create(
            desk=self.desk,
            publication_dt=datetime(self.today.year, self.today.month, 1),
            channel=None
        )
        self.display_calendar(item.title)
        self.display_tooltip(item.title)
        self.check_content_label(['# :', 'Titre :', 'Type :', 'En ligne :', 'Hors-ligne :'])

    def test_tooltip_with_full_info(self):
        self.desk.item_languages_enabled = True
        self.desk.allowed_languages = [u'fr_FR', u'en_US']
        self.desk.save()
        target = targets_factories.TargetFactory(desk=self.desk)
        project = projects_factories.ProjectFactory.create(desk=self.desk)
        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        owner = user_factories.PilotUserFactory()
        self.desk.users.add(owner)
        item = items_factories.ItemFactory.create(
            desk=self.desk,
            project=project,
            channel=channel,
            targets=[target],
            owners=[owner],
            language='fr_FR',
            publication_dt=datetime(self.today.year, self.today.month, 1))

        self.display_calendar(item.title)
        self.display_tooltip(item.title)
        self.check_content_label([u'# :', u'Titre :', u'Type :',
                                  u'Projet :', u'Canal :', u'Cibles :', u'Langue :',
                                  u'Etat :', u'En ligne :', u'Hors-ligne :'])

    def test_with_unpublish_on_same_month(self):
        item = items_factories.ItemFactory.create(
            desk=self.desk,
            publication_dt=datetime(self.today.year, self.today.month, 1),
            state_dates={'unpublished': datetime(self.today.year, self.today.month, 2).strftime('%Y-%m-%d'),
                         'published': datetime(self.today.year, self.today.month, 1).strftime('%Y-%m-%d')}
        )
        self.display_calendar(item.title)
        self.check_nb_item_in_calendar(2, item.title)

    def test_with_unpublish_on_different_month(self):
        published_date = datetime(self.today.year, self.today.month, 1)
        #get a day in the 2 next month
        unpublished_date = published_date + timedelta(days=63)
        item = items_factories.ItemFactory.create(
            desk=self.desk,
            publication_dt=published_date,
            state_dates={'unpublished': unpublished_date.strftime('%Y-%m-02'),
                         'published': published_date.strftime('%Y-%m-%d')}
        )
        self.display_calendar(item.title)
        self.check_nb_item_in_calendar(1, item.title)

        current_month = self.browser.find_element_by_css_selector('.calendar h2').text
        next_month = self.browser.find_element_by_css_selector('.fc-icon-right-single-arrow')
        next_month.click()
        next_month.click()
        WebDriverWait(self.browser, 3).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.calendar'), item.title)
        )
        #Check the displayed month have change to be sure that the displayed item is the correct one
        self.check_nb_item_in_calendar(1, item.title)
        displayed_month = self.browser.find_element_by_css_selector('.calendar h2').text
        self.assertNotEqual(displayed_month, current_month)

    def test_item_without_title(self):
        item = items_factories.ItemFactory.create(
            desk=self.desk,
            publication_dt=datetime(self.today.year, self.today.month, 1),
            channel=None,
            json_content={'title': ''}
        )
        self.display_calendar('Contenu sans titre')
        self.display_tooltip('#')

        calendar_text = self.browser.find_element_by_css_selector('.calendar').text
        self.assertEqual(1, calendar_text.count('Contenu sans titre'))

        self.check_content_label(['# :', 'Titre :', 'Type :', 'En ligne :', 'Hors-ligne :'])
