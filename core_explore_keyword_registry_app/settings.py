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

XSL_FOLDER_PATH = getattr(
    settings, "XSL_FOLDER_PATH", "core_explore_keyword_registry_app/xsl"
)
""" str: Xsl folder path used for the initialisation.
"""

LIST_XSL_FILENAME = getattr(settings, "LIST_XSL_FILENAME", "registry-list.xsl")
"""" str : List xsl filename used for the initialisation.
"""

DETAIL_XSL_FILENAME = getattr(settings, "DETAIL_XSL_FILENAME", "registry-detail.xsl")
"""  str : Detail xsl filename used for the initialisation.
"""
