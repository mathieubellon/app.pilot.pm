

# Does the user has the permission to see a private item, and to edit the private flag ?
def user_has_private_item_perm(user, item):
    if user.is_anonymous:
        return False

    return (
        user == item.created_by or
        user.permissions.is_admin or
        user in item.owners.all()  # not efficient to query each time, should we cache ?
    )


# Is the user allowed to access an item ( read/write ) ?
# Return false when the item is private and the user don't have the permission.
def user_can_access_item(request, item):
    if request.user.is_anonymous:
        return False

    return (
        not request.desk.private_items_enabled or
        not item.is_private or
        user_has_private_item_perm(request.user, item)
    )