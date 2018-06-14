"""Core Explore Keyword App views
"""

from core_explore_keyword_app.views.user.views import KeywordSearchView
from core_explore_keyword_registry_app.views.user.forms import RefinementForm


class KeywordSearchRegistryView(KeywordSearchView):
    @staticmethod
    def _load_assets():
        assets = KeywordSearchView._load_assets()

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

    @staticmethod
    # FIXME: Use get and post functions to handle the refinement form.
    def _load_context(search_form, error, display_persistent_query_button):
        context = KeywordSearchView._load_context(search_form, error,
                                                  display_persistent_query_button)
        context.update({'refinement_form': RefinementForm()})

        return context
