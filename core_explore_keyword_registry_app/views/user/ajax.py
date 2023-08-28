""" Explore keyword registry user ajax
"""

import json
import re
from collections import defaultdict, deque
from itertools import groupby
from logging import getLogger

from django.conf import settings as conf_settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.html import escape
from django.views.generic import View

from core_explore_common_app.components.query import api as query_api
from core_explore_common_app.utils.query import query as query_utils
from core_explore_keyword_app.views.user.ajax import (
    SuggestionsKeywordSearchView,
)
from core_explore_keyword_registry_app.views.user.views import (
    update_content_not_deleted_status_criteria,
)
from core_main_app.rest.data.views import ExecuteLocalQueryView
from core_main_registry_app.components.category import api as category_api
from core_main_registry_app.components.refinement import api as refinement_api
from core_main_registry_app.components.template import (
    api as template_registry_api,
)
from core_main_registry_app.constants import CATEGORY_SUFFIX

if conf_settings.MONGODB_INDEXING:
    from core_main_app.components.mongo import api as main_mongo_api

if "core_explore_oaipmh_app" in conf_settings.INSTALLED_APPS:
    from core_explore_common_app.utils.oaipmh import oaipmh as oaipmh_utils
    from core_oaipmh_harvester_app.rest.oai_record.views import (
        ExecuteQueryView as OaiExecuteQueryView,
    )
    from core_oaipmh_harvester_app.utils.query.mongo.query_builder import (
        OaiPmhAggregateQueryBuilder,
    )

    if conf_settings.MONGODB_INDEXING:
        from core_oaipmh_harvester_app.components.mongo import (
            api as oai_harvester_mongo_api,
        )

logger = getLogger(__name__)


class SuggestionsKeywordRegistrySearchView(SuggestionsKeywordSearchView):
    """Suggestions Keyword Registry Search View"""

    def _get_query_prepared(self, keywords, query_id, request, template_ids):
        """Prepare the query for suggestions.

        Args:
            keywords:
            query_id:
            request:
            template_ids:
        Returns:
        """

        query = super()._get_query_prepared(
            keywords, query_id, request, template_ids
        )

        # Set visibility option for local data source
        query_api.set_visibility_to_query(query, request.user)

        content = json.loads(query.content)

        # Only not DELETED records
        update_content_not_deleted_status_criteria(content)

        # Update content
        query.content = json.dumps(content)

        return query


class RefinementCountView(View):
    """Refinement count."""

    id_key = "_id"
    count_key = "count"
    ids_key = "ids"
    data_field = "dict_content"
    unknown_value = "Unknown"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query = None
        self.match = None
        self.unwind = None
        self.group = None
        self.request = None
        self.results = []

    def get(self, request, *args, **kwargs):
        """get
        Args:
            request

        Returns:

        """
        try:
            if not conf_settings.MONGODB_INDEXING:
                return HttpResponseBadRequest(
                    "MongoDB Data indexing is required. Set MONGODB_INDEXING=True."
                )
            # Get the query
            query_id = request.GET.get("query_id", None)
            self.request = request
            self.query = query_api.get_by_id(query_id, request.user)
            # Build the count
            self.build_count()
        except Exception as exception:
            return HttpResponseBadRequest(
                f"Something wrong happened: {escape(str(exception))}"
            )

        return HttpResponse(json.dumps(self.results), "application/javascript")

    def build_count(self):
        """Count the number of records corresponding to each refinement.

        Returns:

        """
        # Get global template.
        template = template_registry_api.get_current_registry_template(
            request=self.request
        )
        # Get refinements.
        refinements = refinement_api.get_all_filtered_by_template_hash(
            template.hash
        )

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
                if query_utils.is_local_data_source(data_source):
                    self._get_local_data(data_source, data_sources_res)

                # OAI-PMH
                elif oaipmh_utils.is_oai_data_source(data_source):
                    self._get_oai_data(data_source, data_sources_res)
                # Not supported
                else:
                    logger.info(
                        "No treatment available for the data source %s, "
                        "%s. Counters will not take into account this data "
                        "source.",
                        data_source["name"],
                        data_source["url_query"],
                    )

            # Create a map to group the results from the data sources by category id
            res_map = defaultdict(list)
            # Formatting results
            for elt in data_sources_res:
                res_map[str(elt.get(self.id_key))].extend(
                    elt.get(self.ids_key)
                )

            self._build_results(categories, res_map)

    def _build_results(self, categories, res_map):
        """Build the results dictionary.

        Args:
            categories:
            res_map:

        Returns:

        """
        # Update results (id: category_id, count: nb_results). Use set() to avoid duplicates.
        for elt in res_map:
            self.results.extend(
                [{self.id_key: elt, self.count_key: len(set(res_map[elt]))}]
            )

        # Take care of the categories' group
        for category in categories:
            # If it's a group category
            if category.value.endswith(CATEGORY_SUFFIX):
                ids = set()
                # Get the all family
                family = category.get_family()
                # Add each count
                for element in family:
                    # Look if we have a count for this element
                    if str(element.id) in res_map:
                        ids.update(res_map[str(element.id)])

                # Add to the list of results
                self.results.extend(
                    [{self.id_key: category.id, self.count_key: len(ids)}]
                )

    def _prepare_pipeline_categories(self, categories):
        """Prepare the pipeline. Unwind the refinement field and group the results by category.

        Args:
            categories:

        Returns:

        """
        ancestor_refinement_path = ".".join(categories[0].path.split(".")[:-1])
        refinement_paths = []

        # Unwind the field.
        self.unwind = (
            '{{ "$unwind" : {{ "path": "${0}.{1}", '
            '"preserveNullAndEmptyArrays": true }} }}'.format(
                self.data_field, ancestor_refinement_path
            )
        )
        for category in categories:
            if category.path not in refinement_paths:
                refinement_paths.append(category.path)
                self.unwind += ","
                self.unwind += (
                    '{{ "$unwind" : {{ "path": "${0}.{1}", '
                    '"preserveNullAndEmptyArrays": true }} }}'.format(
                        self.data_field, category.path
                    )
                )
        self.project = (
            '{{"$project": {{"__id": "${2}", "{2}": {{"$let": {{"vars":{{ {0} }},"in": {1}'
            " }}}}}}}}".format(
                self._add_categories_name(categories),
                self._add_category(deque(categories)),
                "mongo_id",
            )
        )

        # Group by category.
        self.group = '{"$group": {"_id": "$mongo_id", "ids": {"$push": "$__id"},"count": { "$sum": 1 }}}'

    def _get_local_data(self, data_source, res):
        """Get local data based on the aggregation.

        Args:
            data_source:
            res:

        Returns:

        """
        local_formatted_query = self._get_local_query(data_source)
        local_pipeline = self._get_pipeline(local_formatted_query)
        res.extend(
            main_mongo_api.aggregate(
                json.loads(local_pipeline), self.request.user
            )
        )

    def _get_local_query(self, data_source):
        """Get local query.

        Args:
            data_source:

        Returns:

        """
        local_formatted_query = ExecuteLocalQueryView().build_query(
            query=self.query.content,
            templates=self.query.templates.all(),
            options=data_source["query_options"],
        )
        return local_formatted_query

    def _get_oai_data(self, data_source, res):
        """Get OAI-PMH data based on the aggregation.

        Args:
            data_source:
            res:

        Returns:

        """
        oai_formatted_query = self._get_oai_query(data_source)
        oai_pipeline = self._get_pipeline(oai_formatted_query)
        res.extend(
            oai_harvester_mongo_api.aggregate(
                (json.loads(oai_pipeline)), self.request.user
            )
        )

    def _get_oai_query(self, data_source):
        """Get OAI-PMH query.

        Args:
            data_source:

        Returns:

        """
        registries = []
        if data_source["query_options"] is not None:
            registries.append(int(data_source["query_options"]["instance_id"]))
        oai_formatted_query = OaiExecuteQueryView(
            query_builder=OaiPmhAggregateQueryBuilder
        ).build_query(
            query=self.query.content,
            templates=[
                {"id": _id}
                for _id in self.query.templates.all().values_list(
                    "id", flat=True
                )
            ],
            registries=json.dumps(registries),
        )
        return oai_formatted_query

    def _get_pipeline(self, formatted_query):
        """Get pipeline.

        Args:
            formatted_query:

        Returns:

        """
        self.match = '{{ "$match":  {0} }}'.format(json.dumps(formatted_query))
        local_pipeline = "[{0}, {1}, {2}, {3}]".format(
            self.match, self.unwind, self.project, self.group
        )
        return local_pipeline

    def _add_categories_name(self, categories):
        """Add categories name to the pipeline.

        Args:
            categories:

        Returns:

        """
        # Group by categories.
        category_map = {
            key: [category for category in group]
            for key, group in groupby(
                categories, lambda category: category.path
            )
        }
        elt = []
        for key in category_map:
            # Need to remove specials characters to get a valid query.
            name = re.sub("[^A-Za-z0-9]+", "", key).lower()
            # Access to the field
            elt += [
                '"{0}":{{"$ifNull": ["${1}.{2}", ""]}}'.format(
                    name, self.data_field, key
                )
            ]
            # Access to the field with #text.
            elt += [
                '"{0}text":{{"$ifNull": ["${1}.{2}.#text", ""]}}'.format(
                    name, self.data_field, key
                )
            ]

        return ",".join(elt)

    def _add_category(self, categories):
        """Add category query. Put all the categories in a switch case.
        Each category will create a switch case which match to its ID

        Args:
            categories:

        Returns:

        """
        switch_head = '{"$switch": {"branches": ['
        switch_cases = []
        end_switch = '], "default": "{0}"}}}}'.format(self.unknown_value)

        while len(categories) > 0:
            # Remove the category.
            category = categories.popleft()
            # Get path
            path = "$${0}".format(
                re.sub("[^A-Za-z0-9]+", "", category.path)
            ).lower()
            path_text = "$${0}text".format(
                re.sub("[^A-Za-z0-9]+", "", category.path)
            ).lower()
            # Get value and group name (category id used here)
            value = category.value
            group_name = category.id

            switch_cases.append(
                '{{ "case": {{"$or": [ {{"$eq": ["{0}","{1}"]}}, {{"$eq": ["{2}","{3}"]}} ] }}, '
                '"then": {4} }}'.format(
                    path, value, path_text, value, group_name
                )
            )

        # Join the switch cases
        cases = ",".join(switch_cases)

        # Handle the default case in the switch
        return switch_head + cases + end_switch
