from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.conf import settings

import sitewide.views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cintranet.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', sitewide.views.IndexView.as_view()),

    url(r'^user/', include('auth.urls', app_name='auth', namespace='auth')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ticketing/api/', include('ticketing.api_urls')),
    url(r'^ticketing/', include('ticketing.urls', app_name='ticketing', namespace='ticketing')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
