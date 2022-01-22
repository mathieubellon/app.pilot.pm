# Generated by Django 2.1.7 on 2020-02-10 12:58
import re
import sys

import bleach

from django.db import migrations

from pilot.utils import noop

LINK_RE = re.compile('<a.+?>(.*?)</a>')
MENTION_RE = re.compile('@(\w+)')

MENTION_GROUP_NAMES = {
    'all': ['all', 'tous'],
    'owners': ['owners', 'responsables'],
    'members': ['members', 'membres'],
    'channelOwners': ['channelOwners', 'responsablesCanaux'],
}
inverted_group_names = {}
for name, i18names in MENTION_GROUP_NAMES.items():
    inverted_group_names.update({i18name: name for i18name in i18names})


def convert_comment_to_prosemirror_doc(text, entities):
    if not text:
        return {}

    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\n\n', '\n')

    paragraph_nodes = []
    for paragraph_string in text.split('\n'):
        if not paragraph_string:
            continue

        linkified = bleach.linkify(paragraph_string, [])
        text_nodes = []

        while True:
            link_match = LINK_RE.search(linkified)
            mention_match = MENTION_RE.search(linkified)

            if not link_match and not mention_match:
                break

            link_start = link_match.start() if link_match else sys.maxsize
            mention_start = mention_match.start() if mention_match else sys.maxsize

            if link_start < mention_start:
                start_index = link_start
                end_index = link_match.end()
                href = link_match.group(1).strip()
                marked_string = {"type": "text", "marks": [{"type": "link", "attrs": {"href": href}}], "text": href}
            else:
                start_index = mention_start
                end_index = mention_match.end()
                mention = mention_match.group(1)
                entity = entities.get(mention)

                if not entity:
                    text_nodes.append({"type":"text", "text":  linkified[:end_index]})
                    linkified = linkified[end_index:]
                    continue

                marked_string = {
                    "type": "text",
                    "marks": [{"type": "mention", "attrs": entity}],
                    "text": f'@{mention}'
                }

            if start_index > 0:
                text_nodes.append({"type": "text", "text": linkified[:start_index]})
            text_nodes.append(marked_string)
            linkified = linkified[end_index:]

        if linkified:
            text_nodes.append({"type":"text", "text": linkified})

        paragraph_nodes.append({"type":"paragraph","content": text_nodes})

    return {"type": "doc", "content": paragraph_nodes}


def migrate_comment_to_rte(apps, schema_editor):
    Comment = apps.get_model('comments', 'Comment')
    Item = apps.get_model('items', 'Item')
    PilotUser = apps.get_model('pilot_users', 'PilotUser')
    Team = apps.get_model('pilot_users', 'Team')
    Desk = apps.get_model('desks', 'Desk')

    base_entities = {}
    for group_name, group_id in inverted_group_names.items():
        base_entities[group_name] = {
            'entity': 'group',
            'id': group_id,
            'uid': f'mention-group-{group_id}'
        }

    for user in PilotUser.objects.iterator():
        base_entities[user.username] = {
            'entity': 'user',
            'id': user.id,
            'uid': f'mention-user-{user.id}'
        }


    # desk_id -> entities
    desk_entities = {}

    for desk in Desk.objects.all():
        entities = base_entities.copy()
        desk_entities[desk.id] = entities

        for team in Team.objects.filter(desk=desk):
            entities[team.name] = {
                'entity': 'team',
                'id': team.id,
                'uid': f'mention-team-{team.id}'
            }

    for comment in Comment.objects.iterator():
        comment.new_comment = convert_comment_to_prosemirror_doc(comment.comment, desk_entities[comment.desk_id])
        comment.save()

    for item in Item.objects.exclude(annotations=None).exclude(annotations={}).iterator():
        entities = desk_entities[item.desk_id]
        for field_annotations in item.annotations.values():
            if not field_annotations:
                continue

            for annotation in field_annotations.values():
                annotation['mainComment']['content'] = convert_comment_to_prosemirror_doc(
                    annotation['mainComment']['text'],
                    entities
                )

                for comment in annotation['comments']:
                    comment['content'] = convert_comment_to_prosemirror_doc(comment['text'], entities)

        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0004_auto_20200207_1004'),
    ]

    operations = [
        migrations.RunPython(migrate_comment_to_rte, noop),
    ]
