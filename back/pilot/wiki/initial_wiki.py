from django.utils.translation import ugettext_lazy as _

from pilot.wiki.models import WikiPage

INITIAL_WIKI_HOME_PAGE = {"type": "doc",  "content": [
    {"type": "paragraph", "content":[{"type":"text","text": _("Grâce au wiki vous pourrez répertorier des informations pour l'équipe comme la charte éditoriale, graphique ou d'autres modes d'emploi utiles.")}]},
    {"type": "paragraph", "content":[{"type":"text","text": _("Vous pouvez éditer cette page directement ou en créer de nouvelles.")}]},
    {"type": "paragraph", "content":[{"type":"text","text": _("Pour avertir l'équipe de la création ou mise à jour d'une page pensez aux commentaires (juste en dessous de la page) et à la mention @tous !")}]},
]}


def init_default_wiki_home_page_for_desk(desk):
    WikiPage.objects.create(
        desk=desk,
        created_by_id=1,
        name="Wiki",
        content=INITIAL_WIKI_HOME_PAGE,
        is_home_page=True
    )
