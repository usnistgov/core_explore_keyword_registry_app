"""Core Explore Keyword App views
"""
from core_explore_keyword_app.views.user.views import KeywordSearchView
from core_explore_keyword_registry_app.views.user.forms import RefinementForm


class KeywordSearchRegistryView(KeywordSearchView):

    def _get(self, user, query_id):
        """ Update the GET context

        Args:
            user:
            query_id:

        Returns:

        """
        context = super(KeywordSearchRegistryView, self)._get(user, query_id)
        # TODO: refill the form with selected values
        context.update({'refinement_form': RefinementForm()})
        return context

    def _post(self, request):
        """ Update the POST context

        Args:
            request:

        Returns:

        """
        context = super(KeywordSearchRegistryView, self)._post(request)
        # TODO: refill the form with selected values
        context.update({'refinement_form': RefinementForm(request.POST)})
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
