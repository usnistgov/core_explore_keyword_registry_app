""" Test views
"""
from unittest.mock import MagicMock, patch, Mock

from django.test import RequestFactory, TestCase, override_settings

from core_explore_keyword_registry_app.views.user.ajax import (
    RefinementCountView,
)
from core_main_app.components.template.models import Template
from core_main_app.utils.tests_tools.MockUser import create_mock_user


class TestRefinementCountView(TestCase):
    """Test Refinement Count View"""

    def setUp(self):
        """setUp

        Returns:

        """
        self.factory = RequestFactory()
        self.user1 = create_mock_user(user_id="1")

    def test_get_oai_query(self):
        """test_get_oai_query

        Returns:

        """
        # Arrange
        request = self.factory.get("core_explore_keyword_refinement_count")
        request.user = self.user1

        data_source = {
            "query_options": {"instance_id": 1},
        }
        query = MagicMock()
        rc_view = RefinementCountView()
        rc_view.query = query
        rc_view.registries = ["test"]

        # Act
        oai_query = rc_view._get_oai_query(data_source=data_source)

        # Assert
        self.assertTrue("registry" in oai_query["$and"][1])

    @patch(
        "core_explore_keyword_registry_app.views.user.ajax.RefinementCountView._get_local_data"
    )
    @patch("core_explore_common_app.utils.query.query.is_local_data_source")
    @patch(
        "core_explore_keyword_registry_app.views.user.ajax.RefinementCountView._prepare_pipeline_categories"
    )
    @patch("core_main_registry_app.components.category.api.get_all")
    @patch(
        "core_main_registry_app.components.refinement.api.get_all_filtered_by_template_hash"
    )
    @patch(
        "core_main_registry_app.components.template.api.get_current_registry_template"
    )
    def test_build_count(
        self,
        mock_get_current_registry_template,
        mock_get_all_filtered_by_template_hash,
        mock_get_all,
        mock_prepare_pipeline_categories,
        mock_is_local_data_source,
        mock_get_local_data,
    ):
        """test_build_count

        Returns:

        """
        # Arrange
        mock_template = Mock(Template)
        mock_get_current_registry_template.return_value = mock_template
        mock_get_all_filtered_by_template_hash.return_value = ["refinement"]
        mock_get_all_response = MagicMock()
        mock_get_all_response.filter.return_value = []
        mock_get_all.return_value = mock_get_all_response
        mock_prepare_pipeline_categories.return_value = None
        mock_is_local_data_source.return_value = True
        mock_get_local_data.return_value = []
        request = self.factory.get("core_explore_keyword_refinement_count")
        request.user = self.user1

        query = MagicMock()
        query.data_sources = {
            "query_options": {"instance_id": 1},
        }
        rc_view = RefinementCountView()
        rc_view.query = query

        # Act
        rc_view.build_count()

        # Assert
        self.assertTrue(mock_get_local_data.called)

    @patch(
        "core_explore_keyword_registry_app.views.user.ajax.RefinementCountView._get_oai_data"
    )
    @patch("core_explore_common_app.utils.oaipmh.oaipmh.is_oai_data_source")
    @patch("core_explore_common_app.utils.query.query.is_local_data_source")
    @patch(
        "core_explore_keyword_registry_app.views.user.ajax.RefinementCountView._prepare_pipeline_categories"
    )
    @patch("core_main_registry_app.components.category.api.get_all")
    @patch(
        "core_main_registry_app.components.refinement.api.get_all_filtered_by_template_hash"
    )
    @patch(
        "core_main_registry_app.components.template.api.get_current_registry_template"
    )
    def test_build_count_oaipmh(
        self,
        mock_get_current_registry_template,
        mock_get_all_filtered_by_template_hash,
        mock_get_all,
        mock_prepare_pipeline_categories,
        mock_is_local_data_source,
        mock_is_oai_data_source,
        mock_get_oai_data,
    ):
        """test_build_count_oaipmh

        Returns:

        """
        # Arrange
        mock_template = Mock(Template)
        mock_get_current_registry_template.return_value = mock_template
        mock_get_all_filtered_by_template_hash.return_value = ["refinement"]
        mock_get_all_response = MagicMock()
        mock_get_all_response.filter.return_value = []
        mock_get_all.return_value = mock_get_all_response
        mock_prepare_pipeline_categories.return_value = None
        mock_is_local_data_source.return_value = False
        mock_is_oai_data_source.return_value = True
        mock_get_oai_data.return_value = []
        request = self.factory.get("core_explore_keyword_refinement_count")
        request.user = self.user1

        query = MagicMock()
        query.data_sources = {
            "query_options": {"instance_id": 1},
        }
        rc_view = RefinementCountView()
        rc_view.query = query

        # Act
        rc_view.build_count()

        # Assert
        self.assertTrue(mock_get_oai_data.called)

    @override_settings(MONGODB_INDEXING=False)
    @override_settings(MONGODB_ASYNC_SAVE=False)
    def test_RefinementCountView_with_mongodb_disabled_returns_http_bad_response(
        self,
    ):
        """test_RefinementCountView_with_mongodb_disabled_returns_http_bad_response

        Returns:

        """
        # Arrange
        request = self.factory.get("core_explore_keyword_refinement_count")
        request.user = self.user1

        # Act
        response = RefinementCountView.as_view()(request)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            b"MongoDB Data indexing is required. Set MONGODB_INDEXING=True.",
        )
