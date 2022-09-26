""" Refinement Form.
"""
from django import forms

from core_main_registry_app.components.category import api as category_api
from core_main_registry_app.components.refinement import api as refinement_api
from core_main_registry_app.components.template import (
    api as template_registry_api,
)
from core_main_registry_app.utils.fancytree.widget import FancyTreeWidget


class RefinementForm(forms.Form):
    """Refinement Form"""

    prefix = "refinement"

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        # Get global template.
        template = template_registry_api.get_current_registry_template(
            request=request
        )
        # Get refinements.
        refinements = refinement_api.get_all_filtered_by_template_hash(
            template.hash
        )
        for refinement in refinements:
            categories = category_api.get_all_filtered_by_refinement_id(
                refinement.id
            )
            self.fields[refinement.slug] = forms.ModelMultipleChoiceField(
                queryset=categories,
                required=False,
                label=refinement.name,
                widget=FancyTreeWidget(queryset=categories, count_mode=True),
            )

            self.fields[refinement.slug].has_selected_values = (
                kwargs.get("data").get(f"{self.prefix}-{refinement.slug}")
                is not None
            )
