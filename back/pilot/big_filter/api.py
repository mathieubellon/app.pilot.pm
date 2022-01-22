from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response
from rest_framework.views import APIView

from pilot.assets.models import Asset
from pilot.channels.models import Channel
from pilot.itemsfilters.models import SavedFilter
from pilot.labels.models import Label, LabelTargetType
from pilot.projects.models import Project


class BaseBigFilterSchemaView(APIView):
    created_by_description = _('Créateurs-trices')
    updated_by_description = _('Dernière modification')

    def get(self, request, *args, **kwargs):
        # Big filter should not be called by an anonymous user
        if request.user.is_anonymous or not request.desk:
            return Response([])

        self.request = request
        self.desk = request.desk
        self.user = request.user
        self.desk_users = self.desk.users.all()
        self.filter_schema = []
        self.build_filter_schema()
        return Response(self.filter_schema)

    def build_filter_schema(self):
        raise NotImplementedError()

    def add_category_spec(self, name, label, type, description, icon_name=None, choices=(), multiple=True):
        spec = dict(
            name=name,
            label=force_text(label),
            type=type,
            description=description,
            icon=icon_name,
            multiple=multiple
        )
        if type == 'list':
            spec['choices'] = []
            for choice in choices:
                spec['choices'].append({'value': choice[0], 'label': choice[1]})

        self.filter_schema.append(spec)

    def add_category_spec_from_queryset(self, name, label, description, queryset, icon_name=None, multiple=True):
        choices = ((object.pk, str(object)) for object in queryset.all())
        self.add_category_spec(name, label, 'list', description, icon_name, choices, multiple)

    def add_boolean_spec(self, name, label, description, icon_name):
        choices = (
            ('True', _('Oui')),
            ('False', _('Non')),
        )
        self.add_category_spec(
            name=name,
            label=label,
            type='list',
            description=description,
            icon_name=icon_name,
            choices=choices,
            multiple=False
        )

    def add_created_by_spec(self):
        self.add_category_spec_from_queryset(
            name='created_by',
            label=_('Créé par'),
            description=self.created_by_description,
            queryset=self.desk_users,
            icon_name='User',
        )

    def add_updated_by_spec(self):
        self.add_category_spec_from_queryset(
            name='updated_by',
            label=_('Mis à jour par'),
            description=self.updated_by_description,
            queryset=self.desk_users,
            icon_name='User',
        )

    def add_owners_spec(self, description=None):
        self.add_category_spec_from_queryset(
            name='owners',
            label=_('Responsable'),
            description=description or _('Responsable'),
            queryset=self.desk_users,
            icon_name='User'
        )

    def add_language_spec(self):
        if self.desk.item_languages_enabled:
            languages = self.desk.build_choices_from_allowed_languages(empty_value='blank')
            self.add_category_spec(
                name='language',
                label=_('Langue'),
                type='list',
                description=_('Langue du contenu'),
                icon_name='Language',
                choices=languages
            )

    def add_channels_spec(self):
        channels = (
            Channel.active_objects
            .filter(desk=self.desk)
            .filter_by_permissions(self.request.user)
        )

        self.add_category_spec_from_queryset(
            name='channels',
            label=_('Canal'),
            description=_('Support de diffusion'),
            queryset=channels,
            icon_name='Channel',
        )

    def add_targets_spec(self):
        self.add_category_spec_from_queryset(
            name='targets',
            label=_('Cible'),
            description=_('Segment d\'audience'),
            queryset=self.desk.targets.all(),
            icon_name='Target',
        )

    def add_project_spec(self):
        projects = (
            Project.active_objects
            .filter(desk=self.desk)
            .filter_by_permissions(self.request.user)
        )

        self.add_category_spec_from_queryset(
            name='project',
            label=_('Projet'),
            description=_('Liste les contenus liés au projet sélectionné'),
            queryset=projects,
            icon_name='Project',
        )

    def add_workflow_state_spec(self):
        self.add_category_spec_from_queryset(
            name='workflow_state',
            label=_('Status'),
            description=_('Etat de workflow des contenus'),
            queryset=self.desk.workflow_states.all(),
            icon_name='Status',
        )

    def add_item_type_spec(self):
        self.add_category_spec_from_queryset(
            name='item_type',
            label=_('Type de contenu'),
            description=_('Gabarit de contenus'),
            queryset=self.desk.item_types.all(),
            icon_name='File',
            multiple=False
        )

    def add_members_spec(self):
        self.add_category_spec_from_queryset(
            name='members',
            label=_('Membre'),
            description=_('Membre du projet'),
            queryset=self.desk_users,
            icon_name='User',
        )

    def add_channels_owners_spec(self):
        self.add_category_spec_from_queryset(
            name='channels_owners',
            label=_('Responsable canal'),
            description=_('Affiche les objets liés aux canaux dont cette personne est responsable'),
            queryset=self.desk_users,
            icon_name='User',
        )

    def add_project_state_spec(self):
        self.add_category_spec(
            name='project_state',
            label=_('État du projet'),
            type='list',
            description=_('Etat de production du projet'),
            icon_name='Project',
            choices=Project.STATES_CHOICES
        )

    def add_labels_spec(self, name, label, description, target_type):
        labels = Label.objects.filter(
            desk=self.desk,
            target_type=target_type
        )
        self.add_category_spec_from_queryset(
            name=name,
            label=label,
            description=description,
            queryset=labels,
            icon_name='Tag',
        )

    def add_on_spec(self):
        self.add_category_spec(
            name='on',
            label=_('Exactement le'),
            type='date',
            description=_('Date de publication exactement le'),
            icon_name='Calendar',
            multiple=False
        )

    def add_created_at_spec(self):
        self.add_category_spec(
            name='created_at',
            label=_('Créé à partir de'),
            type='date',
            description=_('Projet créé à partir de cette date'),
            icon_name='Calendar',
            multiple=False
        )


class AssetBigFilterSchema(BaseBigFilterSchemaView):
    created_by_description = _('Créateur-trice du média')
    updated_by_description = _('Dernière modification sur le média')

    def build_filter_schema(self):
        self.add_filetype_spec()
        self.add_folder_spec()
        self.add_created_by_spec()
        self.add_updated_by_spec()

    def add_filetype_spec(self):
        self.add_category_spec(
            name='filetype',
            label=_('Type de fichier'),
            type='list',
            description=_('Image, Pdf, ...'),
            icon_name='File',
            choices=Asset.FILETYPE_CHOICES,
            multiple=False
        )

    def add_folder_spec(self):
        self.add_labels_spec(
            name='folder',
            label=_('Dossier'),
            description=_('Dossier'),
            target_type=LabelTargetType.ASSET_FOLDER
        )


class ChannelBigFilterSchema(BaseBigFilterSchemaView):
    created_by_description = _('Créateur-trice du canal')
    updated_by_description = _('Dernière modification sur le canal')

    def build_filter_schema(self):
        self.add_channel_types_spec()
        self.add_channel_owners_spec()
        self.add_created_by_spec()
        self.add_updated_by_spec()

    def add_channel_types_spec(self):
        self.add_labels_spec(
            name='type',
            label=_('Type'),
            description=_('Type de canal'),
            target_type=LabelTargetType.CHANNEL_TYPE
        )

    def add_channel_owners_spec(self):
        self.add_owners_spec(
            description=_('Responsable du canal')
        )



class ProjectBigFilterSchema(BaseBigFilterSchemaView):
    created_by_description = _('Créateur-trice du projet')
    updated_by_description = _('Dernière modification sur le projet')

    def build_filter_schema(self):
        self.add_start_spec()
        self.add_end_spec()
        self.add_created_at_spec()
        self.add_channels_spec()
        self.add_targets_spec()
        self.add_project_owners_spec()
        self.add_channels_owners_spec()
        self.add_members_spec()
        self.add_created_by_spec()
        self.add_updated_by_spec()
        self.add_project_priority_spec()
        self.add_project_category_spec()
        self.add_project_tags_spec()
        self.add_idea_state_spec()


    def add_start_spec(self):
        self.add_category_spec(
            name='start',
            label=_('Début après le'),
            type='date',
            description=_('Date de début de projet supérieure ou égale à ce filtre'),
            icon_name='Calendar',
            multiple=False
        )

    def add_end_spec(self):
        self.add_category_spec(
            name='end',
            label=_('Fin avant le'),
            type='date',
            description=_('Date de fin de projet inférieure ou égale à ce filtre'),
            icon_name='Calendar',
            multiple=False
        )
    
    def add_project_owners_spec(self):
        self.add_owners_spec(
            description=_('Responsable du projet')
        )

    def add_project_priority_spec(self):
        self.add_labels_spec(
            name='priority',
            label=_('Priorité'),
            description=_('Priorité'),
            target_type=LabelTargetType.PROJECT_PRIORITY
        )

    def add_project_category_spec(self):
        self.add_labels_spec(
            name='category',
            label=_('Catégorie'),
            description=_('Catégorie'),
            target_type=LabelTargetType.PROJECT_CATEGORY
        )

    def add_project_tags_spec(self):
        self.add_labels_spec(
            name='tags',
            label=_('Tag'),
            description=_('Etiquette/Tag'),
            target_type=LabelTargetType.PROJECT_TAGS
        )

    def add_idea_state_spec(self):
        idea_states = Project.STATES_CHOICES[0:2]
        self.add_category_spec(
            name='state',
            label=_('Etat de proposition'),
            type='list',
            description=_('Etat de proposition'),
            icon_name='ProjectSuggested',
            choices=idea_states,
            multiple=False
        )


class ItemListBigFilterSchema(BaseBigFilterSchemaView):
    created_by_description = _('Créateur-trice du contenu')
    updated_by_description = _('Dernière modification sur le contenu')

    def build_filter_schema(self):
        context = self.request.query_params.get('context')
        is_project = context == 'project'
        is_channel = context == 'channel'

        if not is_project:
            self.add_project_spec()
        if not is_channel:
            self.add_channels_spec()
        self.add_targets_spec()
        self.add_workflow_state_spec()
        self.add_item_type_spec()
        self.add_language_spec()
        if not is_project:
            self.add_project_state_spec()
        self.add_item_owners_spec()
        if not is_project:
            self.add_project_owners_spec()
        if not is_channel:
            self.add_channels_owners_spec()
        self.add_created_by_spec()
        self.add_updated_by_spec()
        self.add_tags_spec()
        self.add_start_spec()
        self.add_end_spec()
        self.add_on_spec()
        self.add_period_spec()

    def add_tags_spec(self):
        self.add_labels_spec(
            name='tags',
            label=_('Tags'),
            description=_('Etiquette/Tag'),
            target_type=LabelTargetType.ITEM_TAGS
        )

    def add_start_spec(self):
        self.add_category_spec(
            name='start',
            label=_('Après le'),
            type='date',
            description=_('Date de publication supérieure ou égale à'),
            icon_name='Calendar',
            multiple=False
        )

    def add_end_spec(self):
        self.add_category_spec(
            name='end',
            label=_('Avant le'),
            type='date',
            description=_('Date de publication inférieure ou égale à'),
            icon_name='Calendar',
            multiple=False
        )
    
    def add_item_owners_spec(self):
        self.add_owners_spec(
            description=_('Responsable du contenu'),
        )

    def add_project_owners_spec(self):
        self.add_category_spec_from_queryset(
            name='project_owners',
            label=_('Responsable projet'),
            description=_('Affiche les contenus liés aux projets dont cette personne est responsable'),
            queryset=self.desk_users,
            icon_name='User'
        )

    def add_period_spec(self):
        period_choices = SavedFilter.PERIOD_CHOICES[1:]
        self.add_category_spec(
            name='period',
            label=_('Période'),
            type='list',
            description=_('Date de publication durant les x jours glissants suivants'),
            icon_name='Calendar',
            choices=period_choices,
            multiple=False
        )


class ItemCalendarBigFilterSchema(BaseBigFilterSchemaView):
    created_by_description = _('Créateur-trice du projet/contenu')
    updated_by_description = _('Dernière modification sur le projet/contenu')

    def build_filter_schema(self):
        self.add_language_spec()
        self.add_channels_spec()
        self.add_targets_spec()
        self.add_project_spec()
        self.add_workflow_state_spec()
        self.add_item_type_spec()
        self.add_project_state_spec()

        self.add_project_owners()
        self.add_item_owners()
        self.add_task_assignees()

        self.add_channels_owners_spec()
        self.add_members_spec()
        self.add_created_by_spec()
        self.add_updated_by_spec()

        self.add_project_priority_spec()
        self.add_project_category_spec()
        self.add_project_tags_spec()
        self.add_item_tags_spec()

    def add_project_owners(self):
        self.add_category_spec_from_queryset(
            name='project_owners',
            label=_('Responsable (Projet)'),
            description=_('Projet dont le responsable est...'),
            queryset=self.desk_users,
            icon_name='User'
        )

    def add_item_owners(self):
        self.add_category_spec_from_queryset(
            name='item_owners',
            label=_('Responsable (Contenu)'),
            description=_('Contenu dont le responsable est...'),
            queryset=self.desk_users,
            icon_name='User'
        )

    def add_task_assignees(self):
        self.add_category_spec_from_queryset(
            name='task_assignees',
            label=_('Responsable (Tâche)'),
            description=_('Tâche dont le responsable est...'),
            queryset=self.desk_users,
            icon_name='User'
        )

    def add_project_priority_spec(self):
        self.add_labels_spec(
            name='priority',
            label=_('Priorité (Projet)'),
            description=_('Priorité'),
            target_type=LabelTargetType.PROJECT_PRIORITY
        )

    def add_project_category_spec(self):
        self.add_labels_spec(
            name='category',
            label=_('Catégorie (Projet)'),
            description=_('Catégorie'),
            target_type=LabelTargetType.PROJECT_CATEGORY
        )

    def add_project_tags_spec(self):
        self.add_labels_spec(
            name='project_tags',
            label=_('Tag (Projet)'),
            description=_('Etiquette/Tag'),
            target_type=LabelTargetType.PROJECT_TAGS
        )

    def add_item_tags_spec(self):
        self.add_labels_spec(
            name='item_tags',
            label=_('Tag (Contenu)'),
            description=_('Etiquette/Tag'),
            target_type=LabelTargetType.ITEM_TAGS
        )
