from django.conf.urls.defaults import patterns, include, url
from library.views import *
from django.views.generic.simple import direct_to_template
import os.path
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

site_media = os.path.join(
    os.path.dirname(__file__), 'site_media'
)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'edmodo.views.home', name='home'),
    # url(r'^edmodo/', include('edmodo.foo.urls')),

    # Admin Site
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Media Site
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': site_media }),

    # Edmodo Site
    (r'^$', index),
    (r'^login/$', custom_login),
    (r'^logout/$', logout),
    (r'^home/$', home),
    (r'^register/$', register),
    (r'^register/success/$', direct_to_template, {'template': 'registration/register_success.html'}),
    (r'^library/v2/$', library)
)
