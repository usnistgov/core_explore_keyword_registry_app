""" Apps file for setting core package when app is ready
"""
import sys

from django.apps import AppConfig

from core_explore_keyword_registry_app.permissions import (
    discover as discover_permissions,
)


class ExploreKeywordRegistryAppConfig(AppConfig):
    """Explore Keyword Registry application settings"""

    name = "core_explore_keyword_registry_app"

    def ready(self):
        """Run when the app is ready.

        Returns:

        """
        if "migrate" not in sys.argv:
            from core_explore_keyword_registry_app import discover as discover_xslt

            discover_xslt.init_xslt()
            discover_permissions.init_permissions(self.apps)
