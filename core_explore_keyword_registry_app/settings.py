""" Settings for core_explore_keyword_registry_app

Settings with the following syntax can be overwritten at the project level:
SETTING_NAME = getattr(settings, "SETTING_NAME", "Default Value")
"""

from django.conf import settings

if not settings.configured:
    settings.configure()

REGISTRY_XSD_FILENAME = getattr(settings, "REGISTRY_XSD_FILENAME", "")
""" str: Registry xsd filename used for the initialisation.
"""
