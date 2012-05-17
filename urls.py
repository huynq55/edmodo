from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from library.views import *
from django.contrib import admin
from settings import MEDIA_ROOT
import os
admin.autodiscover()

site_media=os.path.join(
    os.path.dirname(__file__),'site_media'
)
storage=MEDIA_ROOT

urlpatterns = patterns('',
    # Static folder
    url(r'^site_media/(?P<path>.*)$','django.views.static.serve',
            {'document_root': site_media }),
    url(r'^storage/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': storage}),

    #Admin doc
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$',main_page),
    url(r'^contact/$',contact),

    #Login , logout ,register
    url(r'^accounts/login/$',login),
    url(r'^accounts/logout/$',logout),
    url(r'^register/$',register),
    #User page
    url(r'^user/(\w+)/$',user_page),
    url(r'^user/(\w+)/profile/$',user_profile),
    url(r'^user/(\w+)/profile_config/$',user_profile_config),
    url(r'^user/(\w+)/profile_image_change/$',user_profile_image_change),
    url(r'^user/(\w+)/password_change/$',user_password_change),
    url(r'^user/(\w+)/books',user_book_page),
    url(r'^user/(\w+)/images',user_image_page),
    url(r'^user/(\w+)/videos',user_video_page),

    #Make Friend
    url(r'^make_friend/$',make_friend),

    #Notifications
    url(r'^user/(\w+)/notifications/$',get_notifications),

    #Friend requests and accept,decline
    url(r'^user/(\w+)/friend_requests/$',get_friend_requests),
    url(r'^user/(\w+)/friend_accept/$',accept_friend),
    url(r'^user/(\w+)/friend_decline/$',decline_friend),

    #Library
    url(r'^books/$',book_page),
    url(r'^images/$',image_page),
    url(r'^videos/$',video_page),
    url(r'^book/(\d+)/$',book),
    url(r'^image/(\d+)/$',image),
    url(r'^video/(\d+)/$',video),

    #Delete
    url(r'^book_delete/(\d+)/$',delete_book),
    url(r'^image_delete/(\d+)/$',delete_image),
    url(r'^video_delete/(\d+)/$',delete_video),

    #Sharing
    url(r'^set_public/(\w+)/(\d+)/$',set_public_media_object),
    url(r'^set_private/(\w+)/(\d+)/$',set_private_media_object),

    #Voting
    url(r'vote/(\w+)/(\d+)/$',save_vote),

    #Upload
    url(r'^upload/(\w+)/$',file_upload),
    #Download book
    url(r'^download/book/(\d+)/$',book_download),

    #Forum
    url(r'^forum/$',mainForum),
    url(r'^forum/(\d+)/$',forum),
    url(r'^thread/(\d+)/$',thread),

    #Thank
    url(r'^thank/(\d+)/$',thank),

    #Search
    url(r'^search/$',search),
    url(r'^search_all/$',search_all),
)
