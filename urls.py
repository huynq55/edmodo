from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from library.views import *
from django.contrib import admin
from settings import MEDIA_ROOT
admin.autodiscover()

site_media=os.path.join(
    os.path.dirname(__file__),'site_media'
)
storage=MEDIA_ROOT

urlpatterns = patterns('',
    # Static folder
    url(r'^site_media/(?P<path>.*)$','django.views.static.serve',
            {'document_root': site_media }),
    (r'^storage/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': storage}),

    #Admin doc
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$',main_page),

    #Login , logout ,register
    url(r'^accounts/login/$',login),
    url(r'^accounts/logout/$',logout),
    url(r'^register/$',register),
    #User page
    url(r'^user/(\w+)/$',user_page),
    url(r'^user/(\w+)/info/$',user_info),
    url(r'^user/(\w+)/profile_config/$',user_profile_config),
    url(r'^user/(\w+)/profile_image_change/$',user_profile_image_change),

    #Library
    url(r'^library/$',library),
    url(r'^library/(\w+)/$',category),
    url(r'^library/(\w+)/(\d+)',book_page),


    #Test cloud
    url(r'^tag_cloud/$',tag_cloud),

    url(r'^upload/(\w+)/$',file_upload),
    url(r'^upload/success/$',file_upload_success),
    url(r'^download/(\d+)/$',file_download),

    url(r'^pdf_display/$',direct_to_template,{'template':'pdf_display.html'}),

    #Forum
    url(r'^forum/$',mainForum),
    url(r'^forum/(\d+)/$',forum),
    url(r'^thread/(\d+)/$',thread),

    #Friend
    url(r'make_friend/$',make_friend),

    #Vote
    url(r'vote/$',save_vote),

    url(r'^video/success/$',AddVideoSuccess),
    url(r'^video/$',VideoPage)

)
