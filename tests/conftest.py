import os
import sys
import django
import pytest
from django.test import RequestFactory


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),"..",))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE","main.settings",)

django.setup()

@pytest.fixture
def rf():
    return RequestFactory()