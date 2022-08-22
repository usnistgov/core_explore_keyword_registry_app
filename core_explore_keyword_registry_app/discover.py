""" discover for core explore keyword registry app
"""
from __future__ import print_function

from os.path import join

from django.contrib.staticfiles import finders

from core_main_app.commons import exceptions
from core_main_app.components.template_xsl_rendering import (
    api as template_xsl_rendering_api,
)
from core_main_app.components.xsl_transformation import api as xslt_transformation_api
from core_main_app.components.xsl_transformation.models import XslTransformation
from core_main_app.system import api as system_api
from core_main_app.utils.file import read_file_content

from core_explore_keyword_registry_app.settings import (
    XSL_FOLDER_PATH,
    LIST_XSL_FILENAME,
    DETAIL_XSL_FILENAME,
    REGISTRY_XSD_FILENAME,
)


def init_xslt():
    """Init the XSLTs. Add XSLTs and the binding with the registry template.

    Returns:

    """
    try:
        # Get or create template
        template_version_manager = _get_registry_template()
        # Get or create XSLTs
        list_xslt = _get_or_create_xslt(LIST_XSL_FILENAME)
        default_detail_xslt = _get_or_create_xslt(DETAIL_XSL_FILENAME)
        list_detail_xslt = [default_detail_xslt]
        # Create binding between template and XSLTs if does not exist
        _bind_template_xslt(
            template_version_manager.current,
            list_xslt,
            default_detail_xslt,
            list_detail_xslt,
        )
    except Exception as exception:
        print("ERROR : Impossible to init the XSLTs. " + str(exception))


def _get_registry_template():
    """Get the registry template.

    Returns:
        Registry Template.

    """
    try:
        return system_api.get_active_global_version_manager_by_title(
            REGISTRY_XSD_FILENAME
        )
    except Exception as exception:
        raise Exception(
            f"Impossible to get the template {REGISTRY_XSD_FILENAME} : {str(exception)}"
        )


def _get_or_create_xslt(filename):
    """Get or create an xslt.

    Args:
        filename: XSLT filename.

    Returns:
        XSLT.

    """
    try:
        return xslt_transformation_api.get_by_name(filename)
    except exceptions.ApiError:
        # Get XSLT.
        list_xslt_path = finders.find(join(XSL_FOLDER_PATH, filename))
        # Read content.
        list_xsl_data = read_file_content(list_xslt_path)
        # Create the XSLT.
        list_xslt = XslTransformation(
            name=filename, filename=filename, content=list_xsl_data
        )
        return xslt_transformation_api.upsert(list_xslt)
    except Exception as exception:
        raise Exception(f"Impossible to add the xslt {filename} : {str(exception)} ")


def _bind_template_xslt(template_id, list_xslt, default_detail_xslt, list_detail_xslt):
    """Bind the registry template with the XSLTs.

    Args:
        template_id: Registry template id.
        list_xslt: List XSLT.
        default_detail_xslt: Detail XSLT.
        list_detail_xslt:

    Returns:

    """

    try:
        template_xsl_rendering_api.get_by_template_id(template_id)
    except exceptions.DoesNotExist:
        template_xsl_rendering_api.add_or_delete(
            template=system_api.get_template_by_id(template_id),
            list_xslt=list_xslt,
            default_detail_xslt=default_detail_xslt,
            list_detail_xslt=list_detail_xslt,
        )
    except Exception as exception:
        raise Exception(
            f"Impossible to bind the template with XSLTs : {str(exception)}"
        )
