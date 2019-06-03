=================================
Core Explore Keyword Registry App
=================================

Exploration by keywords for the registry core project.

Quickstart
==========

1. Add "core_explore_keyword_app", "core_explore_keyword_registry_app" and "core_explore_common_app" to your INSTALLED_APPS setting
-----------------------------------------------------------------------------------------------------------------------------------
Order matters. Overriding of templates in core_explore_keyword_registry_app.

.. code:: python

    INSTALLED_APPS = [
        ...
        "core_explore_keyword_registry_app", # /!\ Should always be before core_explore_keyword_app, core_explore_common_app
        "core_explore_keyword_app",
        "core_explore_common_app",
    ]

2. Include the core_explore_keyword_registry_app URLconf in your project urls.py
--------------------------------------------------------------------------------

.. code:: python

   url(r'^explore/keyword/', include("core_explore_keyword_registry_app.urls")),
