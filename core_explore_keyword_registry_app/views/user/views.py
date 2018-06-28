"""Core Explore Keyword App views
"""
import json

import core_main_registry_app.utils.refinement.mongo_query as mongo_query_api
from core_explore_common_app.components.query import api as query_api
from core_explore_common_app.constants import LOCAL_QUERY_NAME
from core_explore_keyword_app.views.user.views import KeywordSearchView
from core_explore_keyword_registry_app.views.user.forms import RefinementForm
from core_main_app.commons.exceptions import DoesNotExist
from core_main_app.utils.query.constants import VISIBILITY_OPTION, VISIBILITY_PUBLIC


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
        if query_id is not None:
            try:
                # get the query id
                query = query_api.get_by_id(query_id)
                # get all keywords back
                refinement_selected_values = mongo_query_api.get_refinement_selected_values_from_query(
                    json.loads(query.content)
                )
                # build the data_form structure
                for key in refinement_selected_values:
                    data_form.update({RefinementForm.prefix + '-' + key: refinement_selected_values[key]})
            except Exception, e:
                context.update({'error': "An unexpected error occurred while loading the query: {}.".format(e.message)})
        context.update({'refinement_form': RefinementForm(data=data_form)})
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

        # validate form, test if no errors occurred in the parent treatment and query_id exists
        if refinement_form.is_valid() and error is None and query_id is not None:
            try:
                query = query_api.get_by_id(query_id)
                # Set visibility option for local data source
                for data_source in query.data_sources:
                    # find local data source
                    if data_source.name == LOCAL_QUERY_NAME:
                        # set visibility to public
                        data_source.query_options = {VISIBILITY_OPTION: VISIBILITY_PUBLIC}
                        break
                content = json.loads(query.content)

                # Only not DELETED records
                content.update(mongo_query_api.add_not_deleted_status_criteria())
                refinements = []

                # get selected refinements (categories)
                for refinement_name, selected_categories in refinement_form.cleaned_data.iteritems():
                    if len(selected_categories) > 0:
                        # Add categories ids
                        refinements.append([x.id for x in selected_categories])

                # generate query
                if len(refinements) > 0:
                    # get refinement query
                    refinement_query = mongo_query_api.build_refinements_query(refinements)
                    # if we have a refinement query
                    if len(refinement_query.keys()) > 0:
                        content.update(refinement_query)

                # Update content
                query.content = json.dumps(content)
                # save query
                query_api.upsert(query)
            except DoesNotExist:
                error = "An unexpected error occurred while retrieving the query."
                context.update({'error': error})
            except Exception, e:
                error = "An unexpected error occurred: {}.".format(e.message)
                context.update({'error': error})

        context.update({'refinement_form': refinement_form})
        return context

    def _load_assets(self):
        """ Update assets structure relative to the registry

        Returns:

        """
        assets = super(KeywordSearchRegistryView, self)._load_assets()

        # add all assets needed
        assets['js'].extend([
            {
                "path": 'core_explore_keyword_registry_app/user/js/search/fancytree.custom.js',
                "is_raw": False
            },
        ])

        assets['css'].extend(['core_explore_keyword_registry_app/user/css/fancytree/fancytree'
                              '.custom.css',])

        return assets
