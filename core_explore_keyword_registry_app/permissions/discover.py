""" Discover rules for core explore keyword registry app
"""
from core_main_app.permissions import rights as main_rights
from core_explore_keyword_app.permissions import (
    rights as explore_keyword_rights,
)


def init_permissions(apps):
    """Initialization of groups and permissions

    Returns:

    """
    try:
        group = apps.get_model("auth", "Group")
        permission = apps.get_model("auth", "Permission")

        # Get or Create the anonymous group
        anonymous_group, created = group.objects.get_or_create(
            name=main_rights.ANONYMOUS_GROUP
        )

        # Get explore keyword permissions
        explore_access_perm = permission.objects.get(
            codename=explore_keyword_rights.EXPLORE_KEYWORD_ACCESS
        )

        # add permissions to anonymous group
        anonymous_group.permissions.add(explore_access_perm)
    except Exception as exception:
        print(
            "ERROR : Impossible to init the permissions for core_explore_keyword_registry_app : "
            "" + str(exception)
        )
