from collections import namedtuple
from django.utils.translation import ugettext_lazy as _

MenuElement = namedtuple('MenuElement', ['name', 'label', 'home_view'])

class Menu:
    DASHBOARD = MenuElement('dashboard', _('Tableau de bord'), 'dashboard')
    ITEMS = MenuElement('items', _('Contenus'), 'ui_items_list')
    PROJECTS = MenuElement('projects', _('Projets'), 'ui_projects_list')
    CALENDAR = MenuElement('calendar', _('Calendrier'), 'ui_main_calendar')
    CHANNELS = MenuElement('channels', _('Canaux'), 'ui_channels_list')
    ASSETS = MenuElement('assets', _('Médias'), 'ui_assets_list')
    ADMIN = MenuElement('admin', _('Admin'), 'ui_desk_edit')

    ALL_MENU_ELEMENTS = (DASHBOARD, ITEMS, PROJECTS, CALENDAR, CHANNELS, ASSETS, ADMIN)


MENU_ELEMENTS_DICT = {element.name: element for element in Menu.ALL_MENU_ELEMENTS}


LOGIN_MENU_CHOICES = [(element.name, element.label) for element in (
    Menu.DASHBOARD,
    Menu.ITEMS,
    Menu.PROJECTS,
    Menu.CALENDAR,
)]
