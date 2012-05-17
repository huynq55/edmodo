from library.forms import *
from django.http import  HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext,Context
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from library.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from django.core.paginator import Paginator
from datetime import *
import operator
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
#from django.core.files.storage import default_storage
#from django.utils import simplejson

def mk_paginator(request,items,num_items):
    """Create and return a paginator"""
    paginator=Paginator(items,num_items)
    try: page= int(request.GET.get('page','1'))
    except ValueError: page=1

    try:
        items=paginator.page(page)
    except (InvalidPage,EmptyPage):
        items = paginator.page(paginator.num_pages)
    return items

def main_page(request):
    return render_to_response('index.html',RequestContext(request,{}))
def are_friends(user,other_user):
    if user.friend_list.filter(friend=other_user).exists():
        return True
    return False

@login_required
def make_friend(request):
    if request.method=='GET':
        from_user=request.user
        to_user=get_object_or_404(User,id=request.GET['id'])
        if from_user is not to_user:
            if not from_user.friend_response_list.filter(to_user=to_user).exists():
                friend_request=Friend_Request.objects.create(
                    to_user=to_user,
                    from_user=from_user,
                )
                friend_request.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@login_required
def accept_friend(request,username):
    if request.user.username==username:
        if request.method=="GET":
            user=request.user
            from_user=get_object_or_404(User,id=request.GET['id'])
            if not user.friend_list.filter(friend=from_user).exists():
                friendship1=Friend.objects.create(
                    host=user,
                    friend=from_user,
                )
                friendship1.save()

                friendship2=Friend.objects.create(
                    host=from_user,
                    friend=user,
                )
                friendship2.save()

                friend_request1=user.friend_request_list.get(from_user=from_user)
                if friend_request1:
                    friend_request1.delete()

                if from_user.friend_request_list.count()>0:
                    friend_request2=from_user.friend_request_list.get(from_user=request.user)
                    if friend_request2:
                        friend_request2.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)

@login_required
def decline_friend(request,username):
    if request.user.username==username:
        if request.method=="GET":
            user=request.user
            from_user=get_object_or_404(User,id=request.GET['id'])

            friend_request1=user.friend_request_list.get(from_user=from_user)
            if friend_request1:
                friend_request1.delete()

            if from_user.friend_request_list.count()>0:
                friend_request2=from_user.friend_request_list.get(from_user=request.user)
                if friend_request2:
                    friend_request2.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)

@login_required
def get_friend_requests(request,username):
    if request.user.username==username:
        friend_request_list=request.user.friend_request_list.all()
        return render_to_response("User/friend_requests_page.html",RequestContext(request,{'friend_request_list':friend_request_list,}))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)

#----------------------------Phan User & User Media-------------------------------#
@login_required
def user_page(request,username):
    other_user = get_object_or_404(User, username=username)
    if other_user==request.user:
        return render_to_response('User/user_page.html',RequestContext(request,{'user':request.user,}))
    else:
        if are_friends(request.user,other_user):
            is_friend=True
            is_friend_request=False
        else:
            is_friend=False
            if other_user.friend_request_list.filter(from_user=request.user).exists():
                is_friend_request=True
            else: is_friend_request=False

        other_user_info=other_user.user_information
        if other_user_info.first_name and other_user_info.last_name:
            other_user_name="%s %s" %(other_user_info.first_name,other_user_info.last_name)
        else: other_user_name=''

        if other_user_info.get_age>0:
            other_user_age=other_user_info.get_age
        else:other_user_age=0

        if other_user_info.gender is None:
            other_user_gender=0
        elif other_user_info.gender:
            other_user_gender=1
        else: other_user_gender= -1

        variables=Context({
            'user':request.user,
            'other_user':other_user,
            'other_user_name':other_user_name,
            'other_user_age':other_user_age,
            'other_user_gender':other_user_gender,
            'other_user_about':other_user_info.about,
            'is_friend':is_friend,
            'is_friend_request':is_friend_request,
        })
        return render_to_response('User/other_user_page.html',variables)




@login_required
def user_book_page(request,username):
    if request.user.username==username:
        user=request.user
        books=user.book_list.all().order_by("-upload_date")
        books=mk_paginator(request,books,5)
        return render_to_response('User/user_book_page.html',RequestContext(request,{'books':books,}))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)

@login_required
def user_image_page(request,username):
    if request.user.username==username:
        user=request.user
        images=user.image_list.all().order_by("-upload_date")
        images=mk_paginator(request,images,5)
        return render_to_response('User/user_image_page.html',RequestContext(request,{'images':images,}))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)

@login_required
def user_video_page(request,username):
    if request.user.username==username:
        user=request.user
        videos=user.video_list.all().order_by("-upload_date")
        videos=mk_paginator(request,videos,5)
        return render_to_response('User/user_video_page.html',RequestContext(request,{'videos':videos,}))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)

#----------------------------Het phan User & User Media-------------------------------#


#----------------------------Phan User Config-------------------------------#
@login_required
def user_profile(request,username):
    if request.user.username==username:
        if request.user.user_information:
            user_info=request.user.user_information
        else : user_info=User_Information.objects.create(user=request.user)

        if user_info.gender is None:
            gender=None
        elif user_info.gender:
            gender='m'
        else: gender='f'

        if user_info.birth_date is None :
            day=None
            month=None
            year=None
        else:
            day=user_info.birth_date.day
            month=user_info.birth_date.month
            year=user_info.birth_date.year
        info_dict={
            'first_name':user_info.first_name,
            'last_name':user_info.last_name,
            'gender':gender,
            'about':user_info.about,
            'day':day,
            'month':month,
            'year':year,
        }
        info_form=UserInfoForm(label_suffix='',initial=info_dict)
        return render_to_response('User/user_profile_page.html',RequestContext(request,{'info_form':info_form}))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)

@login_required
def user_profile_config(request,username):
    if request.user.username==username:
        user=request.user
        if request.method=="POST":
            info_form=UserInfoForm(request.POST)
            if info_form.is_valid():
                user_info=user.user_information

                user_info.first_name=info_form.cleaned_data['first_name']
                user_info.last_name=info_form.cleaned_data['last_name']

                gender=info_form.cleaned_data['gender']
                if gender=='m':user_info.gender=True
                if gender=='f': user_info.gender=False

                day=int(info_form.cleaned_data['day'])
                month=int(info_form.cleaned_data['month'])
                year=int(info_form.cleaned_data['year'])

                try:
                    birth_date=date(year,month,day)
                    user_info.birth_date=birth_date
                except ValueError:
                    user_info.birth_date=None

                user_info.about=info_form.cleaned_data['about']
                user_info.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)

#Co van de
@login_required
def user_password_change(request,username):
    status=''
    if request.user.username==username:
        if request.method=='POST':
            password_change_form=PasswordChangeForm(request.POST,label_suffix='')
            if password_change_form.is_valid():
                old_password=password_change_form.cleaned_data['old_password']
                new_password=password_change_form.cleaned_data['new_password1']
                if request.user.check_password(old_password):
                    request.user.set_password(new_password)
                    request.user.save()
                    status='Your password has been changed successfully!'
                else:
                    status='Your old password is not correct!'
            else:
                status='The form is invalid!'
        else:
            password_change_form=PasswordChangeForm(label_suffix='')
        return render_to_response('User/user_password_change_page.html',RequestContext(request,{'password_change_form':password_change_form,'status':status,}))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)

#Co van de
@login_required
def user_profile_image_change(request,username):
    if request.user.username==username:
        status=''
        user_info=request.user.user_information
        if request.method=='POST':
            image_change_form=ProfileImageChangeForm(request.POST,request.FILES)
            if image_change_form.is_valid():
                profile_image=image_change_form.cleaned_data['profile_image']
                new_profile_image=User_Profile_Image.objects.create(
                    user=request.user,
                    profile_image=profile_image,
                )
                new_profile_image.save()
                user_info.avatar_url=new_profile_image.profile_image.url
                user_info.save()
                status="Your profile image has been successfully uploaded!"
            else:
                status="Your form is invalid!"
        image_change_form=ProfileImageChangeForm(label_suffix='')
        avatar_url=user_info.avatar_url
        return render_to_response('User/user_profile_image_change_page.html',RequestContext(request,{'form':image_change_form,'avatar_url':avatar_url,'status':status,}))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)
#----------------------------Het phan User Config-------------------------------#

#-------------------------Phan login,logout,register-------------------------#

def login(request):
    status=''
    if request.user.username:
        return HttpResponseRedirect("/user/%s" %request.user.username)
    else:
        if request.method== "POST":
            login_form=LoginForm(request.POST,label_suffix='')
            if login_form.is_valid():
                login_username=login_form.cleaned_data['username']
                login_password=login_form.cleaned_data['password']
                user = auth.authenticate(username=login_username, password=login_password)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/user/'+login_username+'/')
                else:
                    status="This user is not exists or you type wrong password !"
            else:
                status="This form is not valid !"
            login_form=LoginForm()

        else :
            login_form=LoginForm(label_suffix='')
        variables= RequestContext(request,{
            'form':login_form,
            'status':status,
        })
        return render_to_response('Account/login_page.html',variables)

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

def register(request):
    auth.logout(request)
    status=''
    if request.method == 'POST':
        form = RegistrationForm(request.POST,label_suffix='')
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            user.save()
            user_info=User_Information.objects.create(
                user=user,
            )
            user_info.save()
            return direct_to_template(request, 'Account/register_successful.html')
        else:
            status="The form is invalid !"
    else:
        form = RegistrationForm(label_suffix='')
    variables = RequestContext(request, {'form': form,'status':status,})
    return render_to_response('Account/register_page.html',variables)

#-------------------------Het phan login,logout,register-------------------------#

#---------------------------Phan upload-----------------------------#
def file_upload(request,upload_type):
    if upload_type=='book':
        return book_upload(request)
    if upload_type=='image':
        return image_upload(request)
    if upload_type=='image_link':
        return image_link_upload(request)
    if upload_type=='video_link':
        return video_link_upload(request)

@login_required
def book_upload(request):
    status=''
    if request.method=='POST':
        form=UploadBookForm(request.POST,request.FILES,label_suffix='')
        if form.is_valid():
            book_title=form.cleaned_data['title']
            book_file=form.cleaned_data['up_file']
            book_description=form.cleaned_data['description']
            if form.cleaned_data['public_share']:book_share=True
            else: book_share=False

            book=Book.objects.create(
                uploader=request.user,
                title=book_title,
                book_file=book_file,
                description=book_description,
                public_share=book_share,
            )
            book.save()
            status='Your book has been successfully uploaded !'
        else: status='Your form is invalid !'
    form=UploadBookForm(label_suffix='')
    variables=RequestContext(request,{
        'form':form,
        'status':status,
    })
    return render_to_response('Upload/book_upload_page.html',variables)

@login_required
def image_upload(request):
    status=''
    if request.method == 'POST':
        form=UploadImageForm(request.POST,request.FILES)
        if form.is_valid():
            image_title=form.cleaned_data['title']
            image_file=form.cleaned_data['up_file']
            image_description=form.cleaned_data['description']
            if form.cleaned_data['public_share']:image_share=True
            else: image_share=False

            image=Image.objects.create(
                title=image_title,
                image_file=image_file,
                uploader=request.user,
                description=image_description,
                public_share=image_share,
            )
            image.save()
            status='Your image has been successfully uploaded !'
        else: status='Your form is invalid !'
    form=UploadImageForm(label_suffix='')
    variables=RequestContext(request,{
        'form':form,
        'status':status,
    })
    return render_to_response('Upload/image_upload_page.html',variables)

@login_required
def image_link_upload(request):
    status=''
    if request.method=='POST':
        form=UploadImageLinkForm(request.POST)
        if form.is_valid():
            image_title=form.cleaned_data['title']
            image_url=form.cleaned_data['link']
            image_description=form.cleaned_data['description']
            if form.cleaned_data['public_share']:image_share=True
            else: image_share=False

            image=Image.objects.create(
                title=image_title,
                url=image_url,
                description=image_description,
                public_share=image_share,
                uploader=request.user,
            )
            image.save()
            status='Your image link has been successfully uploaded !'
        else: status='Your form is invalid !'
    form=UploadImageLinkForm(label_suffix='')
    variables=RequestContext(request,{
        'form':form,
        'status':status,
    })
    return render_to_response("Upload/image_link_upload_page.html",variables)

@login_required
def video_link_upload(request):
    status=''
    if request.method == 'POST':
        form=UploadVideoLinkForm(request.POST)
        if form.is_valid():
            video_title=form.cleaned_data['title']
            video_url=form.cleaned_data['link']
            video_description=form.cleaned_data['description']
            if form.cleaned_data['public_share']:video_share=True
            else: video_share=False

            video = Video.objects.create(
                title=video_title,
                url=video_url,
                uploader=request.user,
                description=video_description,
                public_share=video_share,

            )
            video.save()
            status='Your video link has been successfully uploaded !'
        else: status='Your form is invalid !'
    form=UploadVideoLinkForm(label_suffix='')
    variables=RequestContext(request,{
        'form':form,
        'status':status,
    })
    return render_to_response('Upload/video_link_upload_page.html',variables)

#---------------------------Het phan upload-----------------------------#


#---------------------------Phan delete ,set public-----------------------------#

@login_required
def delete_book(request,book_id):
    book=get_object_or_404(Book,id=book_id)
    if book.uploader==request.user:
        book.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@login_required
def delete_image(request,image_id):
    image=get_object_or_404(Image,id=image_id)
    if image.uploader==request.user:
        image.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@login_required
def delete_video(request,video_id):
    video=get_object_or_404(Video,id=video_id)
    if video.uploader==request.user:
        video.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@login_required
def set_public_media_object(request,media_object_type,media_object_id):
    media_object=None
    if media_object_type=='book':
        media_object=get_object_or_404(Book,id=media_object_id)
    if media_object_type=='image':
        media_object=get_object_or_404(Image,id=media_object_id)
    if media_object_type=='video':
        media_object=get_object_or_404(Video,id=media_object_id)
    if media_object:
        media_object.public_share=True
        media_object.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@login_required
def set_private_media_object(request,media_object_type,media_object_id):
    media_object=None
    if media_object_type=='book':
        media_object=get_object_or_404(Book,id=media_object_id)
    if media_object_type=='image':
        media_object=get_object_or_404(Image,id=media_object_id)
    if media_object_type=='video':
        media_object=get_object_or_404(Video,id=media_object_id)
    if media_object:
        media_object.public_share=False
        media_object.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

#---------------------------Het phan delete,set public-----------------------------#


#------------------------Phan Forum---------------------------#
@login_required
def mainForum(request):
    forums = Forum.objects.all()
    return render_to_response("Forum/forum_list_page.html", RequestContext(request,{'forums':forums, 'user':request.user,}))

@login_required
def forum(request,id):
    if request.method=='POST':
        create_thread(request,id)
    forum=get_object_or_404(Forum,id=id)
    threads = Thread.objects.filter(forum=forum).order_by("-created")
    threads = mk_paginator(request, threads,10)
    forum_title=forum.title
    new_thread_form=NewThreadForm(label_suffix='')
    return render_to_response("Forum/thread_list_page.html",RequestContext(request, {'threads':threads,'new_thread_form':new_thread_form,'forum_title':forum_title}))

@login_required
def thread(request,id):
    if request.method=='POST':
        create_post(request,id)
    thread=get_object_or_404(Thread,id=id)
    posts=Post.objects.filter(thread=thread).order_by("created")
    posts=mk_paginator(request,posts,10)
    thread_title=thread.title
    #Luu lai thoi diem truy cap cuoi cung
    #Co participated_thread_set nhung so luong bang 0 (Tuc chua tham gia forum nao)
    if request.user.participated_thread_set.count()>0:
        try:
            participated_thread=request.user.participated_thread_set.get(thread=thread)
            participated_thread.last_modify=datetime.now()
            participated_thread.save()
        except ObjectDoesNotExist:
            pass
    new_post_form=NewPostForm(label_suffix='')
    return render_to_response("Forum/thread.html",RequestContext(request, {'posts':posts,'thread_title':thread_title,'new_post_form':new_post_form}))

@login_required
def create_post(request,id):
    thread=get_object_or_404(Thread,id=id)
    new_post_form=NewPostForm(request.POST)
    if new_post_form.is_valid():
        new_post=Post.objects.create(
            creator=request.user,
            created=datetime.now(),
            thread=thread,
            content=new_post_form.cleaned_data['content'],
            link = new_post_form.cleaned_data['attach_link'],
        )
        new_post.save()

        if not thread.participant_set.filter(participant=request.user).exists():
            new_thread_participant=Thread_Participant.objects.create(
                thread=thread,
                participant=request.user,
                last_modify=datetime.now()
            )
            new_thread_participant.save()
        else :
            thread_participant=thread.participant_set.get(participant=request.user)
            thread_participant.last_modify=datetime.now()
            thread_participant.save()

@login_required
def create_thread(request,id):
    forum=get_object_or_404(Forum,id=id)
    new_thread_form=NewThreadForm(request.POST)
    if new_thread_form.is_valid():
        new_thread=Thread.objects.create(
            creator=request.user,
            created=datetime.now(),
            forum=forum,
            title=new_thread_form.cleaned_data['subject'],
        )
        new_thread.save()

        new_thread_participant=Thread_Participant.objects.create(
            thread=new_thread,
            participant=request.user,
            last_modify=datetime.now()
        )
        new_thread_participant.save()

@login_required
def get_notifications(request,username):
    if request.user.username==username:
        participated_thread_set=request.user.participated_thread_set.all()
        total_notifications=[]
        if participated_thread_set.count()>0:
            for participated_thread in participated_thread_set:
                posts=participated_thread.thread.post_set.filter(created__gt=participated_thread.last_modify)
                notifications=[(post,participated_thread) for post in posts ]
                total_notifications.extend(notifications)
            total_notifications=sorted(total_notifications, key=lambda notification: notification[0].created)
            total_notifications=mk_paginator(request,total_notifications,15)
        return render_to_response('User/user_notifications_page.html',RequestContext(request,{'total_notifications':total_notifications,}))
    else:
        return HttpResponseRedirect('/user/%s' %request.user.username)

#Dinh lam them ajax nhung chua hoan thien boi phai thay doi bien queryset trong javascipt,
# mot viec rat mat thoi gian
#------------------------Het phan Forum---------------------------#

def has_voted(user,media_object):
    if media_object.__class__==Book:
        for voted_book in user.voted_book_set.all():
            if voted_book==media_object: return True
        return False
    if media_object.__class__==Image:
        for voted_image in user.voted_image_set.all():
            if voted_image==media_object: return True
        return False
    if media_object.__class__==Video:
        for voted_video in user.voted_video_set.all():
            if voted_video==media_object: return True
        return False
    return False

def save_vote(request,media_object_type,media_object_id):
    if media_object_type=='book':
        book=get_object_or_404(Book,id=media_object_id)
        book.voters.add(request.user)
        request.user.voted_book_set.add(book)
    if media_object_type=='image':
        image=get_object_or_404(Image,id=media_object_id)
        image.voters.add(request.user)
        request.user.voted_image_set.add(image)
    if media_object_type=='video':
        video=get_object_or_404(Video,id=media_object_id)
        video.voters.add(request.user)
        request.user.voted_video_set.add(video)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

def has_viewed(user,media_object):
    if media_object.__class__==Book:
        for viewed_book in user.viewed_book_set.all():
            if viewed_book==media_object: return True
        return False
    if media_object.__class__==Image:
        for viewed_image in user.viewed_image_set.all():
            if viewed_image==media_object: return True
        return False
    if media_object.__class__==Video:
        for viewed_video in user.viewed_video_set.all():
            if viewed_video==media_object: return True
        return False
    return False
#------------------------Cac trang book ,image, video trong library-------------------#
def book_page(request):
    books=Book.objects.all().order_by("-upload_date")
    books=mk_paginator(request,books,15)
    return render_to_response('Book/books_page.html',RequestContext(request,{'books':books,}))
def image_page(request):
    images=Image.objects.all().order_by("-upload_date")
    images=mk_paginator(request,images,15)
    return render_to_response('Image/images_page.html',RequestContext(request,{'images':images,}))
def video_page(request):
    videos=Video.objects.all().order_by("-upload_date")
    videos=mk_paginator(request,videos,15)
    return render_to_response('Video/videos_page.html',RequestContext(request,{'videos':videos,}))

@login_required
def book(request,book_id):
    book=get_object_or_404(Book,id=book_id)
    if book.public_share or request.user==book.uploader or are_friends(request.user,book.uploader):
        if request.user==book.uploader: is_user=True
        else: is_user=False
        is_voted=has_voted(request.user,book)
        if not has_viewed(request.user,book):
            book.viewers.add(request.user)
            request.user.viewed_book_set.add(book)
        return render_to_response('Book/book.html',RequestContext(request,{'book':book,'is_voted':is_voted,'is_user':is_user,'is_shared':True,}))
    else:
        return render_to_response('Book/book.html',RequestContext(request,{'book':book,'is_shared':False,}))

@login_required
def image(request,image_id):
    image=get_object_or_404(Image,id=image_id)
    if image.public_share or request.user==image.uploader or are_friends(request.user,image.uploader):
        if request.user==image.uploader: is_user=True
        else: is_user=False
        is_voted=has_voted(request.user,image)
        if not has_viewed(request.user,image):
            image.viewers.add(request.user)
            request.user.viewed_image_set.add(image)
        return render_to_response('Image/image.html',RequestContext(request,{'image':image,'is_voted':is_voted,'is_user':is_user,'is_shared':True,}))
    else:
        return render_to_response('Image/image.html',RequestContext(request,{'image':image,'is_shared':False,}))

@login_required
def video(request,video_id):
    video=get_object_or_404(Video,id=video_id)
    if video.public_share or request.user==video.uploader or are_friends(request.user,video.uploader):
        if request.user==video.uploader: is_user=True
        else: is_user=False
        is_voted=has_voted(request.user,video)
        if not has_viewed(request.user,image):
            video.viewers.add(request.user)
            request.user.viewed_video_set.add(video)
        return render_to_response('Video/video.html',RequestContext(request,{'video':video,'is_voted':is_voted,'is_user':is_user,'is_shared':True,}))
    else:
        return render_to_response('Video/video.html',RequestContext(request,{'video':video,'is_shared':False,}))
#------------------------Het cac trang book ,image, video trong library-------------------#

def search(request):
    searched_books=set()
    searched_images=set()
    searched_videos=set()
    query_word_set=None
    show_result=False
    status=''
    if request.GET.has_key('query'):
        search_form=SearchForm(request.GET)
        query=request.GET['query'].strip()
        query_word_set=query.split()
        if request.GET.has_key('book_search'):
            for query_word in query_word_set:
                books=Book.objects.all().filter(title__icontains=query_word)
                searched_books.update(books)

        if request.GET.has_key('image_search'):
            for query_word in query_word_set:
                images=Image.objects.all().filter(title__icontains=query_word)
                searched_images.update(images)
        if request.GET.has_key('video_search'):
            for query_word in query_word_set:
                videos=Video.objects.all().filter(title__icontains=query_word)
                searched_videos.update(videos)
        status='Here is your search result:'
        show_result=True
    else:search_form=SearchForm()
    variables={
        'search_form':search_form,
        'status':status,
        'show_result':show_result,
        'query_word_set':query_word_set,
        'searched_books':searched_books,
        'searched_images':searched_images,
        'searched_videos':searched_videos,
        }
    return render_to_response('Search/search_page.html',RequestContext(request,variables))

def search_all(request):
    if request.method=='POST':
        query=request.POST['query']
        if query:
            return HttpResponseRedirect('/search/?query=%s&book_search=on&image_search=on&video_search=on' %query)
        else:
            return HttpResponseRedirect('/search/')
    else:
        return HttpResponseRedirect('/search/')

@login_required
def book_download(request,book_id):
    book=get_object_or_404(Book,id=book_id)
    downloaded_file=book.book_file
    response=HttpResponse(FileWrapper(downloaded_file), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' %downloaded_file.name.split('/')[-1]
    return response

def thank(request,post_id):
    post=get_object_or_404(Post,id=post_id)
    if post.creator is not request.user:
        if not post.thank_set.filter(from_user=request.user).exists():
            new_thank=Thank.objects.create(
                post=post,
                to_user=post.creator,
                from_user=request.user,
            )
            new_thank.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

def contact(request):
    return render_to_response('contact.html',RequestContext(request,{'user':request.user,}))
