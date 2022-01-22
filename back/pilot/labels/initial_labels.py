from django.utils.translation import ugettext_lazy as _

from pilot.labels.models import Label, LabelTargetType

INITIAL_LABELS = {
    LabelTargetType.ASSET_RIGHT_MEDIUM: (
        dict(
            name=_("Affichage"),
            color='#263238',
            background_color='#CFD8DC',
        ),
        dict(
            name=_("Film (web)"),
            color='#263238',
            background_color='#CFD8DC',
        ),
        dict(
            name=_("Film (TV)"),
            color='#263238',
            background_color='#CFD8DC',
        ),
        dict(
            name=_("Print (Magazine)"),
            color='#263238',
            background_color='#CFD8DC',
        ),
        dict(
            name=_("Print (Dépliant)"),
            color='#263238',
            background_color='#CFD8DC',
        ),
        dict(
            name=_("Web"),
            color='#263238',
            background_color='#CFD8DC',
        ),
    ),

    LabelTargetType.CHANNEL_TYPE:  (
        dict(
            name=_("Sites web"),
            color='#ECEFF1',
            background_color='#37474F',
        ),
        dict(
            name=_("Print"),
            color='#263238',
            background_color='#CFD8DC',
        ),
        dict(
            name=_("Facebook"),
            color='#E8EAF6',
            background_color='#283593',
        ),
        dict(
            name=_("Twitter"),
            color='#E3F2FD',
            background_color='#1565C0',
        ),
        dict(
            name=_("Evènement"),
            color='#FBE9E7',
            background_color='#D84315',
        ),
    ),

    LabelTargetType.PROJECT_PRIORITY:   (
        dict(
            name=_("Priorité haute"),
            color='#FFEBEE',
            background_color='#C62828',
        ),
        dict(
            name=_("Priorité moyenne"),
            color='#FFF8E1',
            background_color='#FF8F00',
        ),
        dict(
            name=_("Priorité normale"),
            color='#263238',
            background_color='#CFD8DC',
        ),
    )

}


def init_labels_for_desk(desk):
    for target_type, initial_labels in INITIAL_LABELS.items():
        for i, dict_state in enumerate(initial_labels):
            Label.objects.create(
                desk=desk,
                created_by_id=1,
                target_type=target_type,
                order=i,
                **dict_state
            )
