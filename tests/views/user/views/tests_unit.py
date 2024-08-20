""" Unit tests for `core_explore_keyword_registry_app.views.user.views` package.
"""

from unittest import TestCase
from unittest.mock import MagicMock, patch

from core_explore_keyword_registry_app.views.user import views as user_views


class TestUpdateContextWithCustomResources(TestCase):
    """Unit tests for `KeywordSearchRegistryView._update_context_with_custom_resources`
    method.
    """

    def setUp(self):
        """setUp"""
        self.mock_kwargs = {"context": MagicMock()}
        self.mock_request = MagicMock()
        self.mock_view = user_views.KeywordSearchRegistryView()
        self.mock_view.request = self.mock_request

    @patch.object(user_views, "custom_resource_api")
    def test_get_current_custom_resource_type_all_called(
        self, mock_custom_resource_api
    ):
        """test_get_current_custom_resource_type_all_called"""
        self.mock_view._update_context_with_custom_resources(
            **self.mock_kwargs
        )

        mock_custom_resource_api.get_current_custom_resource_type_all.assert_called_with(
            request=self.mock_request
        )

    @patch.object(user_views, "custom_resource_api")
    def test_get_all_of_current_template_called(
        self, mock_custom_resource_api
    ):
        """test_get_all_of_current_template_called"""
        self.mock_view._update_context_with_custom_resources(
            **self.mock_kwargs
        )

        mock_custom_resource_api.get_all_of_current_template.assert_called_with(
            request=self.mock_request
        )

    @patch.object(user_views, "custom_resource_api")
    @patch.object(user_views, "json")
    def test_is_custom_resource_type_resource_called(
        self, mock_json, mock_custom_resource_api
    ):
        """test_is_custom_resource_type_resource_called"""
        mock_json.dumps.return_value = MagicMock()

        mock_custom_resource = MagicMock()
        mock_query_set = MagicMock()
        mock_query_set.order_by.return_value = [mock_custom_resource]
        mock_custom_resource_api.get_all_of_current_template.return_value = (
            mock_query_set
        )

        self.mock_view._update_context_with_custom_resources(
            **self.mock_kwargs
        )

        mock_custom_resource_api._is_custom_resource_type_resource.assert_called_with(
            mock_custom_resource
        )

    @patch.object(user_views, "custom_resource_api")
    @patch.object(user_views, "json")
    def test_context_update_called(self, mock_json, mock_custom_resource_api):
        """test_context_update_called"""
        mock_json_dumps = MagicMock()
        mock_json.dumps.return_value = mock_json_dumps

        mock_custom_resource = MagicMock()
        mock_query_set = MagicMock()
        mock_query_set.order_by.return_value = [mock_custom_resource]
        mock_custom_resource_api.get_all_of_current_template.return_value = (
            mock_query_set
        )

        mock_cr_type_all = MagicMock()
        mock_custom_resource_api.get_current_custom_resource_type_all.return_value = (
            mock_cr_type_all
        )

        self.mock_view._update_context_with_custom_resources(
            **self.mock_kwargs
        )

        self.mock_kwargs["context"].update.assert_called_with(
            {
                "custom_resources": [mock_custom_resource],
                "display_not_resource": True,
                "role_custom_resource_type_all": mock_cr_type_all.slug,
                "dict_category_role": mock_json_dumps,
                "dict_refinements": mock_json_dumps,
            }
        )
