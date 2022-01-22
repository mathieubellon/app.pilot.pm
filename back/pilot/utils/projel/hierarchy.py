from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db import transaction

from pilot.channels.models import Channel
from pilot.queue import jobs_registar
from pilot.queue.jobs import Job
from pilot.queue.rq_setup import medium_priority_queue
from pilot.utils.projel.models import Projel


class NodeTypes:
    ITEM = 'item'
    FOLDER = 'folder'


def find_folder_by_name(nodes, folder_name):
    for node in nodes:
        if node['type'] == NodeTypes.FOLDER and node['name'] == folder_name:
            return node
    return None


def get_items_in_folder(nodes, folder_path):
    for folder_name in folder_path:
        folder = find_folder_by_name(nodes, folder_name)
        if not folder:
            return []
        nodes = folder['nodes']

    return [node['id'] for node in folder['nodes'] if node['type'] == NodeTypes.ITEM]


def get_items_paths(nodes, parent_path=[]):
    """
    Returns a dict {item_id: path} for those nodes, recursively,
    with path as an array of folder names : ['folder', 'subfolder', ...]
    """
    items_paths = {}
    for node in nodes:
        if node['type'] == NodeTypes.FOLDER:
            items_paths.update(get_items_paths(node['nodes'], parent_path + [node['name']]))

        elif node['type'] == NodeTypes.ITEM:
            items_paths[node['id']] = parent_path

    return items_paths

def remove_item_from_hierarchy(nodes, item_id):
    """
    Mutate a hierarchy to remove the item node object that correspond to the given item_id
    """
    # Folder are always positionned at the start of the nodes list.
    # We want to check for the items first, so we iterate in reverse
    for i in reversed(range(len(nodes))):
        node = nodes[i]

        if node['type'] == NodeTypes.ITEM and node.get('id') == item_id:
            # We found it, stop the recursive search
            return nodes.pop(i)

        if node['type'] == NodeTypes.FOLDER:
            # Item has not been found in this folder, search in the subfolders
            found = remove_item_from_hierarchy(node['nodes'], item_id)
            if found:
                # If we found the item and removed, there's no need to continue the search, bail out now.
                return found


def set_item_path_in_hierarchy(hierarchy, item, folder_path):
    # The item may be already present somewhere else in the hierarchy
    remove_item_from_hierarchy(hierarchy, item.id)

    # Now we can safely add it at its new location
    nodes = hierarchy
    for folder_name in folder_path:
        folder = find_folder_by_name(nodes, folder_name)
        if not folder:
            return
        nodes = folder['nodes']

    nodes.append({
        'type': NodeTypes.ITEM,
        'id': item.id
    })


def apply_picked_channels(item, picked_channels):
    if not picked_channels:
        return

    for picked_channel in picked_channels:
        channel = Channel.objects.get(pk=picked_channel['channelId'])
        folder_path = picked_channel['folderPath'] or []
        set_item_path_in_hierarchy(channel.hierarchy, item, folder_path)
        channel.save()


def sort_hierarchy(nodes, items):
    def get_sort_key(node):
        if node['type'] == NodeTypes.FOLDER:
            return 'A' + str(node.get('name', ''))
        if node['type'] == NodeTypes.ITEM:
            return 'B' + str(items[node['id']].get('title', ''))

    nodes.sort(key=get_sort_key)


def add_item_to_hierarchy_root(projel, item_id):
    projel.hierarchy.append({
        'type': NodeTypes.ITEM,
        'id': item_id
    })


def walk_nodes_to_see_items(nodes, items):
    for i in reversed(range(len(nodes))):
        node = nodes[i]

        if node['type'] == NodeTypes.ITEM:
            item_id = node.get('id')
            try:
                items.pop(item_id)
            except KeyError:
                nodes.pop(i)

        if node['type'] == NodeTypes.FOLDER:
            # Walk in the subfolders
            walk_nodes_to_see_items(node['nodes'], items)


# Note : the verb "consistentize" does not exists in proper english :-(
def ensure_consistent_hierarchy(projel):
    # We use a transaction + a select_for_update() to ensure we won't override
    # a save made by the frontend
    with transaction.atomic():
        projel = projel.__class__.objects.select_for_update().get(id=projel.id)

        items_queryset = projel.items.values('id', title=KeyTextTransform('title', 'json_content'))
        items = {item['id']: item for item in items_queryset}
        # Make a copy, we'll need the original, untouched items dict for sorting
        unseen_items = dict(items)
        walk_nodes_to_see_items(projel.hierarchy, unseen_items)
        for item_id in unseen_items.keys():
            add_item_to_hierarchy_root(projel, item_id)
        sort_hierarchy(projel.hierarchy, items)
        projel.save()


def projels_for_item(item):
    if item.project:
        return set([item.project]) | set(item.channels.all())
    else:
        return set(item.channels.all())


class HierarchyConsistencyJob(Job):
    job_type = jobs_registar.JOB_TYPE_HIERARCHY_CONSISTENCY
    queue = medium_priority_queue
    delete_tracker_on_success = True

    def run(self, projels):
        # Can also launch the job with a single Projel instead of a iterable
        if isinstance(projels, Projel):
            projels = [projels]

        for projel in projels:
            ensure_consistent_hierarchy(projel)

    @classmethod
    def launch_for_item(cls, request, item):
        cls.launch_r(request, projels_for_item(item))



