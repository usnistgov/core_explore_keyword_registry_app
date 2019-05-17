import json
import re
from collections import defaultdict
from collections import deque
from itertools import groupby
from logging import getLogger

from bson.json_util import dumps, loads
from core_explore_common_app.components.query import api as query_api
from core_explore_common_app.constants import LOCAL_QUERY_NAME
from core_main_app.components.data import api as data_api
from core_main_app.rest.data.views import ExecuteLocalQueryView
from core_main_registry_app.components.category import api as category_api
from core_main_registry_app.components.refinement import api as refinement_api
from core_main_registry_app.components.template import api as template_registry_api
from core_main_registry_app.utils.refinement.tools.tree import TreeInfo
from core_oaipmh_harvester_app.components.oai_record import api as oai_record_api
from core_oaipmh_harvester_app.rest.oai_record.views import ExecuteQueryView as OaiExecuteQueryView
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View

from core_explore_keyword_app.views.user.ajax import SuggestionsKeywordSearchView
from core_explore_keyword_registry_app.views.user.views import update_content_not_deleted_status_criteria

logger = getLogger(__name__)


class SuggestionsKeywordRegistrySearchView(SuggestionsKeywordSearchView):
    """

    """
    def _get_query_prepared(self, keywords, query_id, request, template_ids):
        """ Prepare the query for suggestions.

        Args:
            keywords:
            query_id:
            request:
            template_ids:
        Returns:
        """

        query = super(SuggestionsKeywordRegistrySearchView, self)._get_query_prepared(keywords,
                                                                                      query_id,
                                                                                      request,
                                                                                      template_ids)

        # Set visibility option for local data source
        query_api.set_visibility_to_query(query)

        content = json.loads(query.content)

        # Only not DELETED records
        update_content_not_deleted_status_criteria(content)

        # Update content
        query.content = json.dumps(content)

        return query


class RefinementCountView(View):
    """ Refinement count. """
    id_key = '_id'
    count_key = 'count'
    ids_key = 'ids'
    data_field = 'dict_content'
    unknown_value = 'Unknown'

    def __init__(self, **kwargs):
        super(RefinementCountView, self).__init__(**kwargs)
        self.query = None
        self.match = None
        self.unwind = None
        self.group = None
        self.request = None
        self.results = []

    def get(self, request, *args, **kwargs):
        try:
            # Get the query
            query_id = request.GET.get('query_id', None)
            self.request = request
            self.query = query_api.get_by_id(query_id)
            # Build the count
            self.build_count()
        except Exception, e:
            return HttpResponseBadRequest("Something wrong happened.")

        return HttpResponse(json.dumps(self.results), 'application/javascript')

    def build_count(self):
        """ Count the number of records corresponding to each refinement.

        Returns:

        """
        # Get global template.
        template = template_registry_api.get_current_registry_template()
        # Get refinements.
        refinements = refinement_api.get_all_filtered_by_template_hash(template.hash)

        # For each refinement
        for refinement in refinements:
            data_sources_res = []
            # Get categories
            categories = category_api.get_all().filter(refinement=refinement)
            # Prepare pipeline
            self._prepare_pipeline_categories(categories)
            # Only selected data provider
            # FIXME: Decouple data source.
            for data_source in self.query.data_sources:
                # find local data source
                if data_source.name == LOCAL_QUERY_NAME:
                    self._get_local_data(data_source, data_sources_res)
                # OAI-PMH
                elif data_source.url_query.endswith(reverse(
                        "core_explore_oaipmh_rest_execute_query")):
                    self._get_oai_data(data_source, data_sources_res)
                # Not supported
                else:
                    logger.info("No treatment available for the data source {0}, "
                                "{1). Counters will not take into account this data "
                                "source.".format(data_source.name, data_source.url_query))

            # Create a map to group the results from the data sources by category id
            res_map = defaultdict(list)
            # Formatting results
            for elt in data_sources_res:
                res_map[elt.get(self.id_key)].extend(elt.get(self.ids_key))

            self._build_results(categories, res_map)

    def _build_results(self, categories, res_map):
        """ Build the results dictionary.

        Args:
            categories:
            res_map:

        Returns:

        """
        # Update results (id: category_id, count: nb_results). Use set() to avoid duplicates.
        for elt in res_map:
            self.results.extend([{self.id_key: elt, self.count_key: len(set(res_map[elt]))}])

        # Take care of the categories' group
        for category in categories:
            # If it's a group category
            if category.value.endswith(TreeInfo.get_category_label()):
                ids = set([])
                # Get the all family
                family = category.get_family()
                # Add each count
                for f in family:
                    # Look if we have a count for this element
                    if str(f.id) in res_map:
                        ids.update(res_map[str(f.id)])

                # Add to the list of results
                self.results.extend([{self.id_key: category.id, self.count_key: len(ids)}])

    def _prepare_pipeline_categories(self, categories):
        """ Prepare the pipeline. Unwind the refinement field and group the results by category.

        Args:
            categories:

        Returns:

        """
        refinement_path = categories[0].path
        ancestor_refinement_path = '.'.join(categories[0].path.split('.')[:-1])
        # Unwind the field.
        self.unwind = '{{ "$unwind" : {{ "path": "${0}.{1}", ' \
                      '"preserveNullAndEmptyArrays": true }} }},' \
                      '{{ "$unwind" : {{ "path": "${0}.{2}", ' \
                      '"preserveNullAndEmptyArrays": true }} }}'.format(self.data_field,
                                                                        ancestor_refinement_path,
                                                                        refinement_path)
        # Group by category.
        self.group = '{{"$group": {{"{2}": {{"$let": {{"vars":{{ {0} }},"in": {1} }}}}' \
                     ',"{4}": {{"$sum": 1}}' \
                     ',"{3}": {{"$push": "${2}"}}' \
                     '}}}}'.format(self._add_categories_name(categories),
                                   self._add_category(deque(categories)),
                                   self.id_key, self.ids_key, self.count_key)

    def _get_local_data(self, data_source, res):
        """ Get local data based on the aggregation.

        Args:
            data_source:
            res:

        Returns:

        """
        local_formatted_query = self._get_local_query(data_source)
        local_pipeline = self._get_pipeline(local_formatted_query)
        res.extend(data_api.aggregate(loads(local_pipeline), self.request.user))

    def _get_local_query(self, data_source):
        """ Get local query.

        Args:
            data_source:

        Returns:

        """
        local_formatted_query = ExecuteLocalQueryView().build_query(query=self.query.content,
                                                                    templates=self.query.templates,
                                                                    options=data_source.query_options)
        return local_formatted_query

    def _get_oai_data(self, data_source, res):
        """ Get OAI-PMH data based on the aggregation.

        Args:
            data_source:
            res:

        Returns:

        """
        oai_formatted_query = self._get_oai_query(data_source)
        oai_pipeline = self._get_pipeline(oai_formatted_query)
        res.extend(oai_record_api.aggregate((loads(oai_pipeline))))

    def _get_oai_query(self, data_source):
        """ Get OAI-PMH query.

        Args:
            data_source:

        Returns:

        """
        registries = []
        if data_source.query_options is not None:
            registries.append(data_source.query_options['instance_id'])
        oai_formatted_query = OaiExecuteQueryView(). \
            build_query(query=self.query.content, templates=json.dumps(self.query.templates),
                        registries=json.dumps(registries))
        return oai_formatted_query

    def _get_pipeline(self, formatted_query):
        """ Get pipeline.

        Args:
            formatted_query:

        Returns:

        """
        self.match = '{{ "$match":  {0} }}'.format(dumps(formatted_query))
        local_pipeline = '[{0}, {1}, {2}]'.format(self.match, self.unwind, self.group)
        return local_pipeline

    def _add_categories_name(self, categories):
        """ Add categories name to the pipeline.

        Args:
            categories:

        Returns:

        """
        # Group by categories.
        category_map = {
            key: [category for category in group]
            for key, group in groupby(categories, lambda category: category.path)
            }
        elt = []
        for key in category_map:
            # Need to remove specials characters to get a valid query.
            name = re.sub('[^A-Za-z0-9]+', '', key).lower()
            # Access to the field
            elt += ['"{0}":{{"$ifNull": ["${1}.{2}", ""]}}'.format(name, self.data_field, key)]
            # Access to the field with #text.
            elt += ['"{0}text":{{"$ifNull": ["${1}.{2}.#text", ""]}}'.format(name,
                                                                             self.data_field, key)]

        return ','.join(elt)

    def _add_category(self, categories):
        """ Add category query. Recursive calls.
        Each category will create a group.

        Args:
            categories:

        Returns:

        """
        # Add unknown case.
        if len(categories) == 0:
            return '"{0}"'.format(self.unknown_value)

        # Remove the category.
        category = categories.popleft()
        # Get path
        path = "$${0}".format(re.sub('[^A-Za-z0-9]+', '', category.path)).lower()
        path_text = "$${0}text".format(re.sub('[^A-Za-z0-9]+', '', category.path)).lower()
        # Get value and group name (category id used here)
        value = category.value
        group_name = category.id

        # Recursive calls to treat all categories.
        return '{{"$cond": [ {{"$or": [ {{"$eq": ["{0}","{1}"]}}, {{"$eq": ["{2}","{3}"]}} ] }}, ' \
               '"{4}",{5}]}}'.format(path, value, path_text, value, group_name,
                                     self._add_category(categories))