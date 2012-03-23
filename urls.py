from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from library.views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

site_media=os.path.join(
    os.path.dirname(__file__),'site_media'
)
urlpatterns = patterns('',
    # Site media
    url(r'^site_media/(?P<path>.*)$','django.views.static.serve',
            {'document_root': site_media }),

    #Admin doc
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$',main_page),

    #Login , logout ,register
    url(r'^login/$',login),
    url(r'^logout/$',logout),
    url(r'^register/$',register),
    #User page
    url(r'^user/(\w+)/$',user_page),
    url(r'^user/(\w+)/config/$',user_config),

    #Library
    url(r'^library/$',library),
    url(r'^library/(\w+)/$',category),
    url(r'^library/(\w+)/(\d+)',book_page),


    #Test cloud
    url(r'^tag_cloud/$',tag_cloud),

    url(r'^upload/$',file_upload),
    url(r'^upload/success/$',file_upload_success),
    url(r'^download/(\d+)/$',file_download),

    url(r'^pdf_display/$',direct_to_template,{'template':'pdf_display.html'}),


)
