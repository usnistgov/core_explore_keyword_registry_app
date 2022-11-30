""" Tests Settings
"""

SECRET_KEY = "fake-key"

INSTALLED_APPS = [
    # Django apps
    "django.contrib.auth",
    "django.contrib.contenttypes",
    # Local apps
    "tests",
]
MONGODB_INDEXING = False
MONGODB_ASYNC_SAVE = False
