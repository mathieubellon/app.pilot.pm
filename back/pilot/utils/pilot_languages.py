from django.utils.translation import ugettext_lazy as _

# Languages can be added in the following dict. The verbose form can be displayed in the UI

LANGUAGES_CHOICES = (
    ('ar', _("Arabe")),
    ('bg_BG', _("Bulgare")),
    ('cs_CZ', _("Tchèque")),
    ('da_DK', _("Danois")),
    ('de_DE', _("Allemand")),
    ('el_GR', _("Grec")),
    ('en_US', _("Anglais")),
    ('es_ES', _("Espagnol")),
    ('et_EE', _("Estonien")),
    ('fi_FI', _("Finnois")),
    ('fr_FR', _("Français")),
    ('hr_HR', _("Japonais")),
    ('hu_HU', _("Hongrois")),
    ('it_IT', _("Italien")),
    ('lt_LT', _("Lituanien")),
    ('ja_JA', _("Japonais")),
    ('nl_NL', _("Néerlandais")),
    ('no_NO', _("Norvégien")),
    ('pl_PL', _("Polonais")),
    ('pt_PT', _("Portugais")),
    ('ro_RO', _("Roumain")),
    ('ru_RU', _("Russe")),
    ('sk_SK', _("Slovaque")),
    ('sl_SI', _("Slovène")),
    ('sv_SE', _("Suédois")),
    ('tr_TR', _("Turc")),
    ('zh_CN', _("Chinois")),
)

LANGUAGES = dict(LANGUAGES_CHOICES)


FR_LANG = 'fr'
EN_LANG = 'en'

PILOT_UI_LANGUAGES = (
    (FR_LANG, 'Français'),
    (EN_LANG, 'English')
)


def validate_user_language(language, default_language=FR_LANG):
    if language in dict(PILOT_UI_LANGUAGES).keys():
        return language
    else:
        return default_language
