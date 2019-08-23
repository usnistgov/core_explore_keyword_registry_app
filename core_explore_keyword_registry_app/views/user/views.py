"""Core Explore Keyword App views
"""
import json

import core_main_registry_app.utils.refinement.mongo_query as mongo_query_api
from core_explore_common_app.commons.exceptions import ExploreRequestError
from core_explore_common_app.components.query import api as query_api
from core_explore_keyword_app.views.user.views import KeywordSearchView
from core_explore_keyword_registry_app.views.user.forms import RefinementForm
from core_main_app.commons.exceptions import DoesNotExist
from core_main_registry_app.components.custom_resource import api as custom_resource_api
from core_main_registry_app.components.refinement import api as refinement_api
from core_main_registry_app.components.template import api as template_registry_api


def update_content_not_deleted_status_criteria(content):
    """ Only not DELETED records.

    Args:
        content:

    Returns:
    """
    content.update(mongo_query_api.add_not_deleted_status_criteria())


class KeywordSearchRegistryView(KeywordSearchView):

    def _get(self, user, query_id):
        """ Update the GET context

        Args:
            user:
            query_id:

        Returns:

        """
        context = super(KeywordSearchRegistryView, self)._get(user, query_id)
        data_form = {}
        refinement_selected_types = []
        category_list = ""
        query_id = context.get("query_id", None)

        # in case we don't find the query id in the context
        # a default query is created by inheritance
        if query_id is None:
            raise ExploreRequestError("query id is missing")

        try:
            # get the query id
            query = query_api.get_by_id(query_id)
            # here we have to make sure to set the visibility and status criteria
            # set visibility
            query_api.set_visibility_to_query(query)
            # load content
            content = json.loads(query.content)
            # update content with status
            update_content_not_deleted_status_criteria(content)
            query.content = json.dumps(content)
            # save query
            query_api.upsert(query)
            # get all keywords back
            refinement_selected_values = mongo_query_api.get_refinement_selected_values_from_query(content)
            # build the data_form structure
            for key in refinement_selected_values:
                for display_name in refinement_selected_values[key]:
                    list_element = refinement_selected_values[key][display_name]
                    data_form.update({RefinementForm.prefix + '-' + key: [element["id"]
                                                                          for element
                                                                          in list_element]})
                    refinement_selected_types = [element["value"] for element in list_element]
                    # create the list of category
                    if len(refinement_selected_values[key]) > 0:
                        category_list = "%s,%s|%s" % (category_list,
                                                      display_name,
                                                      key)
                    context.update({'category_list': category_list})
        except Exception as e:
            context.update({'error': "An unexpected error occurred while loading the query: {}.".format(str(e))})

        context.update({'refinement_form': RefinementForm(data=data_form)})
        # get all categories which must be selected in the table
        context.update({'refinement_selected_types': refinement_selected_types})

        # Custom registry
        self._update_context_with_custom_resources(context)
        return context

    def _post(self, request):
        """ Update the POST context

        Args:
            request:

        Returns:

        """
        context = super(KeywordSearchRegistryView, self)._post(request)
        # get refinement form
        refinement_form = RefinementForm(data=request.POST)
        # get query_id and error from the context
        error = context.get("error", None)
        query_id = context.get("query_id", None)
        refinement_selected_types = []

        # validate form, test if no errors occurred in the parent treatment and query_id exists
        if refinement_form.is_valid() and error is None and query_id is not None:
            try:
                query = query_api.get_by_id(query_id)
                content = json.loads(query.content)
                refinements = []
                # Update content with status
                update_content_not_deleted_status_criteria(content)
                # get selected refinements (categories)
                for refinement_name, selected_categories in list(refinement_form.cleaned_data.items()):
                    if len(selected_categories) > 0:
                        # Add categories ids
                        refinements.append([x.id for x in selected_categories])

                # generate query
                if len(refinements) > 0:
                    # get refinement query
                    refinement_query = mongo_query_api.build_refinements_query(refinements)
                    # if we have a refinement query
                    if len(list(refinement_query.keys())) > 0:
                        content.update(refinement_query)

                # Update content
                query.content = json.dumps(content)
                # save query
                query_api.upsert(query)
            except DoesNotExist:
                error = "An unexpected error occurred while retrieving the query."
                context.update({'error': error})
            except Exception as e:
                error = "An unexpected error occurred: {}.".format(str(e))
                context.update({'error': error})

        context.update({'refinement_form': refinement_form})

        # get all categories which must be selected in the table
        if refinement_form.cleaned_data:
            # get the current template
            template = template_registry_api.get_current_registry_template()
            # get the refinement 'Type'
            refinement = refinement_api.get_by_template_hash_and_by_slug(template.hash, 'type')
            # get the selected_types
            selected_types = refinement_form.cleaned_data.get(refinement.slug, None)
            # create the list of type
            if selected_types:
                refinement_selected_types = get_all_parent_name_from_category_list(selected_types)
            # create the list of category
            category_list = ""
            for key in refinement_form.cleaned_data:
                if len(refinement_form.cleaned_data[key]) > 0:
                    category_list = "%s,%s|%s" % (category_list,
                                                  refinement_form.cleaned_data[key][0].refinement.name,
                                                  key)
            context.update({'category_list': category_list})

        # get all categories which must be selected in the table
        context.update({'refinement_selected_types': refinement_selected_types})
        # Custom registry
        self._update_context_with_custom_resources(context)
        return context

    def _update_context_with_custom_resources(self, context):
        """ Update the context with custom resources.

        Args:
            context:
        Returns:
        """
        # TODO: use custom_resource to get cr_type_all
        cr_type_all = custom_resource_api.get_current_custom_resource_type_all()
        custom_resources = list(
            custom_resource_api.get_all_of_current_template().order_by('sort'))
        dict_category_role = {}
        dict_refinements = {}
        for cr in custom_resources:
            if custom_resource_api._is_custom_resource_type_resource(cr) and cr.display_icon:
                dict_category_role[cr.role_type.split(':')[0]] = cr.slug
            dict_refinements[cr.slug] = cr.refinements if len(cr.refinements) > 0 else []
        context.update({
            'custom_resources': custom_resources,
            'display_not_resource': True,  # display all resource
            'role_custom_resource_type_all': cr_type_all.slug,
            'dict_category_role': json.dumps(dict_category_role),
            'dict_refinements': json.dumps(dict_refinements)
        })

    def _load_assets(self):
        """ Update assets structure relative to the registry

        Returns:

        """
        assets = super(KeywordSearchRegistryView, self)._load_assets()

        # add all assets needed
        assets['js'].extend([
            {
                "path": "core_explore_keyword_registry_app/user/js/search/tagit.custom.js",
                "is_raw": False
            },
            {
                "path": "core_explore_keyword_registry_app/user/js/search/fancytree.custom.js",
                "is_raw": False
            },
            {
                "path": "core_explore_keyword_registry_app/user/js/search/resource_type_icons_table.js",
                "is_raw": False
            },
            {
                "path": "core_explore_keyword_registry_app/user/js/search/filters.js",
                "is_raw": False
            },
        ])

        assets['css'].extend(["core_explore_keyword_registry_app/user/css/fancytree/fancytree.custom.css",
                              "core_main_registry_app/user/css/resource_banner/selection.css",
                              "core_main_registry_app/user/css/resource_banner/resource_banner.css",
                              "core_explore_keyword_registry_app/user/css/search/filters.css"])

        return assets


def get_all_parent_name_from_category_list(categories):
    """ Get the first parent name's list from a category list given

    Args:
        categories:

    Returns:

    """
    parents = []
    for category in categories:
        parent = category.get_root().name
        if parent not in parents:
            parents.append(parent)
    return parents
