from django.http import *
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
from settings import MEDIA_ROOT
from django.core.paginator import Paginator
from easy_thumbnails.files import *
from PIL import Image

ITEMS_PER_CATEGORY_PAGE=1

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
    categories=Category.objects.all()
    shared_books=Book.objects.filter(public_share=True)
    top_read=shared_books.order_by('-read_count')[:5]
    top_downloaded=shared_books.order_by('downloader_set.count')[:5]
    top_like=shared_books.order_by('vote_set.count')[:5]
    return render_to_response('index.html', RequestContext(request,
        {'categories':categories,
         'top_read':top_read,
         'top_downloaded':top_downloaded,
         'top_like':top_like,
        }))

def has_friend(user,other_user):
    for friend in user.friend_list.all():
        if friend.friend_id==other_user.id:
            return True
    return False

def make_friend(request):
    if request.method=='GET':
        friend_id=request.GET['id']
        new_friend=Friend.objects.create(
            host=request.user,
            friend_id=friend_id,
        )
        new_friend.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@login_required
def user_page(request,username):
    other_user = get_object_or_404(User, username=username)
    if request.user==other_user:
        is_user=True
        is_friend=False
    else:
        is_user=False
        if has_friend(request.user,other_user): is_friend=True
        else: is_friend=False

    variables=Context({
        'user':request.user,
        'other_user':other_user,
        'is_user':is_user,
        'is_friend':is_friend,
    })
    return render_to_response('User/user_page.html', variables)

@login_required
def user_password_change(request,username):
    user = get_object_or_404(User, username=username)
    user_info=user.user_information
    status=''
    if request.method=='POST':
        password_change_form=PasswordChangeForm(request.POST)
        if password_change_form.is_valid():
            old_password=password_change_form.cleaned_data['old_password']
            new_password=password_change_form.cleaned_data['new_password1']
            if user.check_password(old_password):
                user.set_password(new_password)
                status='Your password has been changed !'
            else:
                status='Your old password is not correct !'
    password_change_form=PasswordChangeForm()
    return render_to_response('password_change_page.html',RequestContext(request,{'form':password_change_form,'status':status}))

@login_required
def user_profile_config(request,username):
    user = get_object_or_404(User, username=username)
    user_info=user.user_information
    first_name=user_info.first_name
    last_name=user_info.last_name
    email=user.email
    if not request.method=='POST':
        form=UserInfoForm(initial={'first_name':first_name,'last_name':last_name,'email':email},label_suffix='')
    else :
        form=UserInfoForm(request.POST,label_suffix='')
    return render_to_response('User/user_config_page.html',RequestContext(request,{'form':form,}))

@login_required
def user_info(request,username):
    user = get_object_or_404(User, username=username)
    user_info=user.user_information
    return render_to_response('User/user_info_page.html',RequestContext(request,{'user_info':user_info,}))

from PIL import Image as PIL_Image
@login_required
def user_profile_image_change(request,username):
    user = get_object_or_404(User, username=username)
    user_info=user.user_information
    status=0
    img=None
    if request.method=='POST':
        image_change_form=ProfileImageChangeForm(request.POST,request.FILES)
        if image_change_form.is_valid():
            profile_img=image_change_form.cleaned_data['profile_image']
            user_info.image=profile_img
            status=1
            user_info.save()
            imfn = '/'.join([MEDIA_ROOT,'kien',profile_img.name])
            im = PIL_Image.open(imfn)
            im.thumbnail((200,200), Image.ANTIALIAS)
            im.save(imfn, "JPEG")

    else :
        status=2
        image_change_form=ProfileImageChangeForm()

    if user_info.image:
        img='/%s/%s' %('storage',user_info.image.url)
    return render_to_response('profile_image_upload_page.html',RequestContext(request,{'form':image_change_form,'img':img,'status':status}))

def login(request):
    status='This is form !'
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
                status="This user is not exits !"
        variables=RequestContext(request,{
            'form':LoginForm(),
            'status':status
        })
        return render_to_response('Authentication/login_page.html',variables)

    else :
        login_form=LoginForm(label_suffix='')
        variables= RequestContext(request,{
            'form':login_form,
            'status':status
        })
        return render_to_response('Authentication/login_page.html',variables)
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

def register(request):
    auth.logout(request)
    if request.method == 'POST':
        form = RegistrationForm(request.POST,label_suffix='')
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            return HttpResponseRedirect('/')
    else:
        form = RegistrationForm(label_suffix='')
    variables = RequestContext(request, {'form': form})
    return render_to_response('Authentication/register.html',variables)

def tag_cloud(request):
    categories=Category.objects.all()
    return render_to_response('tag_cloud.html',RequestContext(request,{
        'categories':categories,
    }))
def file_upload(request,upload_type):
    if upload_type=='book':
        return book_upload(request)
    if upload_type=='image':
        return image_upload(request)
    if upload_type=='video':
        return AddVideo(request)

def book_upload(request):
    if request.method=='POST':
        form=UploadFileForm(request.POST,request.FILES,label_suffix='')
        if form.is_valid():
            #uploadedFile = request.FILES['up_file']
            uploaded_file=form.cleaned_data['up_file']
            file_description=form.cleaned_data['description']
            file_category=form.cleaned_data['category']
            file_share=form.cleaned_data['public_share']

            file_name=uploaded_file.name

            created_book=Book.objects.create(
                title=file_name,
                category=file_category,
                file=uploaded_file,
                #thumbnail=thumbnail,
                uploader=request.user,
                description=file_description,
                public_share=file_share,
            )
            created_book.save()
            #thumbnail_option={'crop': True, 'size': (160, 120),}
            #thumbnail=ThumbnailerFieldFile(created_book.file)
            #created_book.thumbnail=thumbnail
            #created_book.save()
            status=4
                #return HttpResponseRedirect('/upload/success/')

            '''
            book,created_book=Book.objects.get_or_create(title=file_name)
            if not created_book :
                status=3
            else :
                created_book.category=file_category
                created_book.file=uploaded_file
                created_book.uploader=request.user
                created_book.description=file_description
                created_book.public_share=file_share
                created_book.save()
                status=4
            '''
        #form=UploadFileForm(label_suffix='')
        #title='a book'
        #return render_to_response('upload_page.html',RequestContext(request,{'form':form,'title':title,'status':status}))

    #else :
    form=UploadFileForm(label_suffix='')
    title='a book'
    status=2
    return render_to_response('upload_page.html',RequestContext(request,{'form':form,'title':title,'status':status}))

def file_upload_success(request):
    return render_to_response('successfully_upload_page.html')

from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
import cStringIO

def file_download(request,book_id):
    book=Book.objects.get(id=int(book_id))
    downloaded_file=book.file
    #Can kiem tra file name, chinh file name thong qua split va splitext

    '''
    #Muon dung stringIO phai mo file ra roi ghi(mat cong,nhung nhanh)
    buffer_output=cStringIO.StringIO()
    for chunk in downloaded_file.chunks():
        buffer_output.write(chunk)
    buffer_output.close()
    response=HttpResponse(buffer_output, content_type='application/pdf')
    '''
    response=HttpResponse(FileWrapper(downloaded_file), content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename=%s' %downloaded_file.name

    return response


def library(request):
    categories=Category.objects.all()
    books={}
    for category in categories:
        book_group=category.book_set.filter(public_share=True)
        books[category.name]=book_group.order_by('-upload_date')[:3]
    return render_to_response('library.html',RequestContext(request,{'categories':categories,'books':books}))

def has_voted(user,book):
    for vote in user.vote_set.all():
        if vote.book==book:return True
    else: return False

def save_vote(request):
    if request.method=='GET':
        book_id=request.GET['id']
        book=get_object_or_404(Book,pk=book_id)
        new_vote=Vote.objects.create(
            voter=request.user,
            book=book,
        )
        new_vote.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

MAIN_FIL='posted_date'
SUB_FIL='dec'
def category(request,category_name):
    if not request.GET:
        return HttpResponseRedirect('/library/%s/?page=1' %category_name)
    else:
        try:
            page=int(request.GET['page'])
        except:
            return Http404
        #return render_to_response('check_page.html',RequestContext(request,{'page':page}))

    page=int(request.GET['page'])
    category=get_object_or_404(Category,name=category_name)

    if request.POST:
        filter_form=FilterForm(request.POST,label_suffix='')
        if filter_form.is_valid():
            main_filter=filter_form.cleaned_data['main_filter']
            sub_filter=filter_form.cleaned_data['sub_filter']
            global MAIN_FIL,SUB_FIL
            MAIN_FIL=main_filter
            SUB_FIL=sub_filter
            filter_form.initial={'main_filter':MAIN_FIL,'sub_filter':SUB_FIL}
    else:
        filter_form=FilterForm(label_suffix='',initial={'main_filter':MAIN_FIL,'sub_filter':SUB_FIL})

    books=book_filter(category,MAIN_FIL,SUB_FIL)

    if books is None:
        status='There are no book in %s category' %category_name
        return render_to_response('Book/category_page.html',RequestContext(request,{'category':category,'status':status}))

    else:
        status='There are %s books in %s category' %(books.count(),category_name)
        '''
        paginator=Paginator(books,ITEMS_PER_CATEGORY_PAGE)
        try:
            current_page_books=paginator.page(page_index)
        except:
            raise Http404
        variables=RequestContext(request,{
            'form':filter_form,
            'category':category,
            'status':status,
            'books':books,
            'current_page_books':current_page_books,
            'show_paginator':paginator.num_pages>1,
            'has_prev':current_page_books.has_previous(),
            'has_next':current_page_books.has_next(),
            'page':page_index,
            'pages':paginator.num_pages,
            'next_page':page_index+1,
            'prev_page':page_index-1,
        })
        '''
        books=mk_paginator(request,books,2)
        #return render_to_response('category_page.html',variables)
        return render_to_response('Book/category_page.html',RequestContext(request,{'category':category,'books':books,'form':filter_form,'page':page}))

def book_page(request,category_name,book_id):
    category=get_object_or_404(Category,name=category_name)
    book=Book.objects.get(id=book_id)
    is_voted=has_voted(request.user,book)
    return render_to_response('Book/book_page.html',RequestContext(request,{'book':book,'is_voted':is_voted}))

def book_filter(category,main_filter,sub_filter):
    books=category.book_set.filter(public_share=True)
    if sub_filter == 'dec':
        if main_filter == 'posted_date':
            books=books.order_by('-upload_date')
            return books
        if main_filter == 'reading_number':
            books=books.order_by('-read_count')
            return books
        if main_filter == 'like_number':
            books=books.order_by('-num_voter')
            return books
        if main_filter == 'file_size':
            #books=books.order_by('-file_size')
            books=sorted(books,key=lambda book:book.book_size(),reverse=True)
            return books
    if sub_filter == 'inc':
        if main_filter == 'posted_date':
            books=books.order_by('upload_date')
            return books
        if main_filter == 'reading_number':
            books=books.order_by('read_count')
            return books
        if main_filter == 'like_number':
            books=books.order_by('num_voter')
            return books
        if main_filter == 'file_size':
            #books=books.order_by('file_size')
            books=sorted(books,key=lambda book:book.book_size())
            return books
def delete_book(request,username,book_id):
    book=get_object_or_404(Book,id=book_id)
    book.delete()
    return HttpResponseRedirect('/')
def delete_image(request,username,image_id):
    image=get_object_or_404(Image,id=image_id)
    image.delete()
    return HttpResponseRedirect('/')
def delete_video(request,username,video_id):
    video=get_object_or_404(Video,id=video_id)
    video.delete()
    return HttpResponseRedirect('/')

def mainForum(request):
    forums = Forum.objects.all()
    return render_to_response("Forum/main_forum.html", RequestContext(request,{'forums':forums, 'user':request.user,}))

def add_csrf(request, ** kwargs):
    d = dict(user=request.user, ** kwargs)
    d.update(csrf(request))
    return d

def forum(request, pk):
    """Listing of threads in a forum."""
    if request.method=='POST':
        create_thread(request,pk)
    threads = Thread.objects.filter(forum=pk).order_by("-created")
    threads = mk_paginator(request, threads, 1)
    new_thread_form=NewThreadForm()
    return render_to_response("Forum/forum.html",RequestContext(request, {'threads':threads,'new_thread_form':new_thread_form}))

def thread(request,pk):
    """Listing posts in a thread"""
    if request.method=='POST':
        create_post(request,pk)
    thread=Thread.objects.get(pk=pk)
    posts=Post.objects.filter(thread=pk).order_by("-created")
    posts=mk_paginator(request,posts,2)
    title=thread.title
    if request.user==thread.creator:
        thread.notification=0
        thread.save()
    reply_form=ReplyForm()
    return render_to_response("Forum/thread.html",RequestContext(request, {'posts':posts,'title':title,'reply_form':reply_form}))

@login_required
def create_post(request,pk):
    reply_form=ReplyForm(request.POST)
    if reply_form.is_valid():
        new_post=Post.objects.create(
            creator=request.user,
            thread=Thread.objects.get(pk=pk),
            content=reply_form.cleaned_data['content'],
            link = reply_form.cleaned_data['attach_link'],
        )
        new_post.save()

        thread=Thread.objects.get(pk=pk)
        thread.notification+=1
        thread.save()

@login_required
def create_thread(request,pk):
    new_thread_form=NewThreadForm(request.POST)
    if new_thread_form.is_valid():
        new_thread=Thread.objects.create(
            creator=request.user,
            forum=Forum.objects.get(pk=pk),
            title=new_thread_form.cleaned_data['subject'],
        )
        new_thread.save()


def AddVideo(request):
    if request.method == 'POST':
        form=AddVideoForm(request.POST)
        if form.is_valid():
            video_url=form.cleaned_data['url']
            video_description=form.cleaned_data['description']
            video_share=form.cleaned_data['public_share']
            video = Video.objects.create(
                url=video_url,
                description=video_description,
                public_share=video_share,
                uploader=request.user,
            )
            video.save()
            return HttpResponseRedirect("/video/success")
        form=AddVideoForm()
    form=AddVideoForm()
    var=RequestContext(request,{
        'form':form
    })
    return render_to_response('Video/add_video.html',var)

def AddVideoSuccess(request):
    return render_to_response('Video/success.html')

def VideoPage(request):
    videos=Video.objects.all()
    var=RequestContext(request,{
        'videos': videos
    })
    return render_to_response('Video/video_page.html', var)
