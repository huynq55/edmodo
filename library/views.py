from django.http import *
from library.forms import *

from django.http import  HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
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
from django.contrib.auth.decorators import login_required
@login_required

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

def main_page(request):
    global state
    state = '..........'

    categories=Category.objects.all()
    shared_books=Book.objects.filter(public_share=True)
    top_read=shared_books.order_by('-read_count')[:5]
    top_downloaded=shared_books.order_by('downloader_set.count')[:5]
    top_like=shared_books.order_by('vote_set.count')[:5]

    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username = username, password = password)
            if user is not None:
                if user.is_active:
                    login(request)
                    return HttpResponseRedirect('/')
            else:
                state ='Username and passowrd didn\'t match. Please try again.!'
                return render_to_response('main_page.html', RequestContext(request,{'state':state}))
    else:
        form = loginForm()

    variables = RequestContext(request, {
        'Main_form': form,
        })
    return render_to_response(
        'main_page.html', variables)

def user_page(request,username):
    user = get_object_or_404(User, username=username)
        #user_image=Image.open(os.path.join(DEFAULT_USER_IMAGE_FOLDER,'male_user.png'))
        #user_image=get_thumbnailer('user_images/male_user.png').generate_thumbnail({'size': (200, 200)})
        #user_image=open(os.path.join(DEFAULT_USER_IMAGE_FOLDER,'male_user.png'))
        #user_image_url=os.path.join(DEFAULT_USER_IMAGE_FOLDER,'male_user.png')
    return render_to_response(
        'user_page.html', RequestContext(request,{'user': user,})
    )


def user_config(request,username):
    user = request.user
    if not request.method=='POST':
        form=UserInfoForm()
    else :
        form=UserInfoForm(request.POST)
    return render_to_response('user_config_page.html',RequestContext(request,{'form':form,}))


def login(request):
    status='This is form !'
    if request.method== "POST":
        login_form=loginForm(request.POST,label_suffix='')
        if login_form.is_valid():
            login_username=login_form.cleaned_data['username']
            login_password=login_form.cleaned_data['password']
            user = auth.authenticate(username=login_username, password=login_password)
            if user is not None and user.is_active:
                auth.login(request, user)
                #status="Welcome "+login_username
                #request.session[login_username]=user.id
                #return HttpResponseRedirect('/user/'+login_username)
                return HttpResponseRedirect('/user/'+login_username+'/')
            else:
                status="This user is not exits !"
        variables=RequestContext(request,{
            'form':loginForm(),
            'status':status
        })
        return render_to_response('login_page.html',variables)

    else :
        login_form=loginForm(label_suffix='')
        variables= RequestContext(request,{
            'form':login_form,
            'status':status
        })
        return render_to_response('login_page.html',variables)

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
            #return HttpResponseRedirect('/register/success/')
            return HttpResponseRedirect('/')
    else:
        form = RegistrationForm(label_suffix='')
    variables = RequestContext(request, {'form': form})
    return render_to_response('register.html',variables)

def tag_cloud(request):
    categories=Category.objects.all()
    return render_to_response('tag_cloud.html',RequestContext(request,{
        'categories':categories,
    }))

def file_upload(request):
    status=0
    if request.method=='POST':
        form=UploadFileForm(request.POST,request.FILES,label_suffix='')
        if form.is_valid():
            #uploadedFile = request.FILES['up_file']
            uploaded_file=form.cleaned_data['up_file']
            file_description=form.cleaned_data['description']
            file_category=form.cleaned_data['category']
            file_share=form.cleaned_data['public_share']

            # the cleaned_data of a FileField is an
            # UploadedFile object. It's a small data container
            # with no methods and just two properties:
            #filename = uploadedFile.filename
            #fileData = uploadedFile.content
            file_name=uploaded_file.name
            '''
            file_thumbnail=Thumbnailer(uploaded_file,"xxx")
            thumbnail_option={'crop': True, 'size': (160, 120),}
            thumbnail=file_thumbnail.get_thumbnail(thumbnail_option)
            '''

            '''
            fd=open('%s/%s'% (MEDIA_ROOT, file_name),'wb+')
            for chunk in uploadedFile.chunks():
                fd.write(chunk)
            fd.close()
            return HttpResponseRedirect('/')
            '''
            try:
                book=Book.objects.get(title=file_name)
            except:
                status=3
                #return HttpResponseRedirect('/')

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
            thumbnail_option={'crop': True, 'size': (160, 120),}
            thumbnail=ThumbnailerFieldFile(created_book.file)
            created_book.thumbnail=thumbnail
            created_book.save()
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
        form=UploadFileForm(label_suffix='')
        return render_to_response('upload_page.html',RequestContext(request,{'form':form,'status':status}))

    else :
        form=UploadFileForm(label_suffix='')
        status=2
        return render_to_response('upload_page.html',RequestContext(request,{'form':form,'status':status}))

def file_upload_success(request):
    return render_to_response('successfully_upload_page.html')
'''
from reportlab.pdfgen import canvas
def pdf_display(request):
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'show; filename=somefilename.pdf'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response
'''

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

def category(request,category_name):
    if not request.GET:
        return HttpResponseRedirect('/library/%s/?page=1' %category_name)
    else:
        try:
            page_index=int(request.GET['page'])
        except:
            return Http404
        #return render_to_response('check_page.html',RequestContext(request,{'page':page}))
    category=get_object_or_404(Category,name=category_name)
    books=None
    if request.method == 'POST':
        return HttpResponseRedirect('/')
        filter_form=FilterForm(request.POST,label_suffix='')
        if filter_form.is_valid():
            main_filter=filter_form.cleaned_data['main_filter']
            sub_filter=filter_form.cleaned_data['sub_filter']
            books=book_filter(category,main_filter,sub_filter)
            return HttpResponseRedirect('/')
            #return render_to_response('check_page.html',RequestContext(request,{'books':books}))
            #if books is None:
                #return render_to_response('check_page.html',RequestContext(request,{'main_filter':main_filter,'sub_filter':sub_filter,}))
    else:
        filter_form=FilterForm()
        books=category.book_set.filter(public_share=True)
        books=books.order_by('-upload_date')

    if books is None:
        status='There are no book in %s category' %category_name
        return render_to_response('category_page.html',RequestContext(request,{'category':category,'status':status}))

    else:
        status='There are %s books in %s category' %(books.count(),category_name)
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
        return render_to_response('category_page.html',variables)
        #return render_to_response('category_page.html',RequestContext(request,{'category':category,'books':books}))

def book_page(request,category_name,book_id):
    category=get_object_or_404(Category,name=category_name)
    book=category.book_set.get(id=int(book_id))
    if not book.public_share:
        raise Http404
    else:
        return render_to_response('book_page.html',RequestContext(request,{'book':book}))

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
            books=books.order_by('-vote_set.count')
            return books
        if main_filter == 'file_size':
            books=books.order_by('-file.size')
            return books
    if sub_filter == 'inc':
        if main_filter == 'posted_date':
            books=books.order_by('upload_date')
            return books
        if main_filter == 'reading_number':
            books=books.order_by('read_count')
            return books
        if main_filter == 'like_number':
            books=books.order_by('vote_set.count')
            return books
        if main_filter == 'file_size':
            books=books.order_by('file.size')
            return books