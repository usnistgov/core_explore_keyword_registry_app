""" Url router for the explore keyword registry application
"""

from django.conf.urls import url
from core_explore_keyword_app.views.user import views as user_views, ajax as user_ajax
from core_explore_keyword_registry_app.views.user import views as registry_views

urlpatterns = [
    url(r'^$', registry_views.KeywordSearchRegistryView.as_view(),
        name='core_explore_keyword_app_search'),
    url(r'^(?P<query_id>\w+)$', registry_views.KeywordSearchRegistryView.as_view(),
        name='core_explore_keyword_app_search'),
    url(r'^get-persistent-query-url$', user_ajax.CreatePersistentQueryUrlKeywordView.as_view(),
        name='core_explore_keyword_get_persistent_query_url'),
    url(r'^results-redirect/(?P<persistent_query_id>\w+)', user_views.ResultQueryRedirectKeywordView.as_view(),
        name='core_explore_keyword_results_redirect'),
]
