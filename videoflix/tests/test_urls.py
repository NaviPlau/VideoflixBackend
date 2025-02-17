from django.test import SimpleTestCase
from django.urls import reverse, resolve
from django.conf import settings
from django.contrib.staticfiles.urls import static
from videoflix.urls import urlpatterns


class UrlsTestCase(SimpleTestCase):
    """Test Django URL configuration"""

    def test_admin_url_resolves(self):
        """Test if the admin panel URL resolves correctly"""
        resolver = resolve("/videoflix/admin/")
        self.assertEqual(resolver.func.__module__, "django.contrib.admin.sites")

    def test_static_files_serving(self):
        """Test if static files are served correctly when DEBUG=True"""
        if settings.DEBUG:
            static_urls = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
            self.assertTrue(len(static_urls) > 0, "Static URLs are not configured properly")
