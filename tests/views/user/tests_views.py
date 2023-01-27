""" Test views
"""
from unittest.mock import MagicMock

from django.test import RequestFactory, TestCase

from core_explore_keyword_registry_app.views.user.ajax import (
    RefinementCountView,
)
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
