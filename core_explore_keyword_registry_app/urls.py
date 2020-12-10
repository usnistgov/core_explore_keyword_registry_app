""" Url router for the explore keyword registry application
"""

from django.urls import re_path, include

from core_explore_keyword_app.views.user import views as user_views, ajax as user_ajax
from core_explore_keyword_registry_app.views.user import ajax as registry_ajax
from core_explore_keyword_registry_app.views.user import views as registry_views

urlpatterns = [
    re_path(
        r"^get-refinement-count",
        registry_ajax.RefinementCountView.as_view(),
        name="core_explore_keyword_refinement_count",
    ),
    re_path(
        r"^suggestions$",
        registry_ajax.SuggestionsKeywordRegistrySearchView.as_view(),
        name="core_explore_keyword_suggestions",
    ),
    re_path(
        r"^$",
        registry_views.KeywordSearchRegistryView.as_view(),
        name="core_explore_keyword_app_search",
    ),
    re_path(
        r"^(?P<query_id>\w+)$",
        registry_views.KeywordSearchRegistryView.as_view(),
        name="core_explore_keyword_app_search",
    ),
    re_path(
        r"^get-persistent-query-url$",
        user_ajax.CreatePersistentQueryUrlKeywordView.as_view(),
        name="core_explore_keyword_get_persistent_query_url",
    ),
    re_path(
        r"^results-redirect",
        user_views.ResultQueryRedirectKeywordView.as_view(),
        name="core_explore_keyword_results_redirect",
    ),
    re_path(r"^rest/", include("core_explore_keyword_app.rest.urls")),
]
