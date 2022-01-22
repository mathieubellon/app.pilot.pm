
class C2S_MESSAGES:
    DELETE_ELASTIC_ELEMENT = 'delete_elastic_element'
    REGISTER_ON_ITEM = 'register_on_item'
    SHARED_ITEM_AUTH = 'shared_item_auth'
    UPDATE_USER_ACTIVITY = 'update_user_activity'
    UPDATE_ITEM_CONTENT = 'update_item_content'


class S2C_MESSAGES:
    BROADCAST_ASSET_CONVERSION_STATUS = 'broadcast_asset_conversion_status'
    BROADCAST_ITEM = 'broadcast_item'
    BROADCAST_ITEM_CHANGES = 'broadcast_item_changes'
    BROADCAST_USERS_ON_ITEM = 'broadcast_users_on_item'
    INVALID_CHANGES = 'invalid_changes'


def get_desk_group(desk_id):
    return f"desk-{desk_id}"


def get_item_group(item_id):
    return f"item-{item_id}"
