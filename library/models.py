from django.db import models
from django.contrib.auth.models import User
from datetime import *

from django.db.models.signals import post_delete
from django.core.files.storage import default_storage
# Create your models here.

def dynamic_upload(instance, filename):
    type=''
    username=''
    if instance.__class__==Book:
        type='books'
        username=instance.uploader.username
    if instance.__class__==Image:
        type='images'
        username=instance.uploader.username
    if instance.__class__==User_Profile_Image:
        type='profile_images'
        username=instance.user.username
    if type :
        return '/'.join([username,type, filename])
    else :
        return '/'.join([username, filename])

class Book(models.Model):
    title=models.CharField(max_length=200)
    uploader=models.ForeignKey(User,related_name='book_list')
    book_file=models.FileField(upload_to=dynamic_upload,blank=True)
    description=models.TextField(blank=True)
    upload_date=models.DateTimeField(auto_now_add=True)
    public_share=models.BooleanField(default=False)
    voters=models.ManyToManyField(User,related_name="voted_book_set")
    viewers=models.ManyToManyField(User,related_name="viewed_book_set")
    def __unicode__(self):
        return u'%s' %self.book_file.name

def delete_filefield(**kwargs):
    book = kwargs.get('instance')
    if book.book_file:
        default_storage.delete(book.book_file.path)
post_delete.connect(delete_filefield, Book)

class Image(models.Model):
    title=models.CharField(max_length=200)
    uploader=models.ForeignKey(User,related_name='image_list')
    image_file=models.ImageField(upload_to=dynamic_upload,blank=True)
    description=models.TextField(blank=True)
    upload_date=models.DateTimeField(auto_now_add=True)
    public_share=models.BooleanField(default=False)
    url = models.URLField(blank=True)
    voters=models.ManyToManyField(User,related_name="voted_image_set")
    viewers=models.ManyToManyField(User,related_name="viewed_image_set")
    def __unicode__(self):
        if self.image_file:
            return u'%s' %self.image_file.name
        else :
            return u'%s' %self.url

def delete_imagefield(**kwargs):
    image = kwargs.get('instance')
    if image.image_file:
        default_storage.delete(image.image_file.path)
post_delete.connect(delete_imagefield, Image)

class Video(models.Model):
    title=models.CharField(max_length=200)
    uploader=models.ForeignKey(User,related_name='video_list')
    description=models.TextField(blank=True)
    upload_date=models.DateTimeField(auto_now_add=True)
    public_share=models.BooleanField(default=False)
    url=models.URLField()
    voters=models.ManyToManyField(User,related_name="voted_video_set")
    viewers=models.ManyToManyField(User,related_name="viewed_video_set")
    def __unicode__(self):
        return u'%s' %self.url

    def get_Youtube_video_id(self):
        Youtube_video_id=str(self.url).split('/')[-1]
        return Youtube_video_id

class User_Information(models.Model):
    user=models.OneToOneField(User)
    first_name=models.CharField(max_length=200,blank=True)
    last_name=models.CharField(max_length=200,blank=True)
    gender=models.NullBooleanField(blank=True)
    birth_date=models.DateField(blank=True,null=True)
    about=models.TextField(blank=True)
    avatar_url=models.URLField(blank=True,default="/site_media/img/default_user_avatar/User.png")

    def __unicode__(self):
        return u'User information of %s' %self.user.username

    def get_age(self):
        age=0
        if self.birth_date: age=datetime.now().year-self.birth_date.year
        return age

class User_Profile_Image(models.Model):
    user=models.ForeignKey(User,related_name="profile_image_set")
    profile_image=models.ImageField(upload_to=dynamic_upload)
    def __unicode__(self):
        return u'Profile image: %s of %s' %(self.profile_image.name,self.user.username)

class Friend(models.Model):
    host=models.ForeignKey(User,related_name="friend_list",db_column="host_user_id")
    friend=models.ForeignKey(User,related_name="host_friend_list",db_column="friend_user_id")

    class Meta:
        unique_together=('host','friend')

    def __unicode__(self):
        return u"%s has friend %s" %(self.host.username,self.friend.username)

class Friend_Request(models.Model):
    to_user=models.ForeignKey(User,related_name="friend_request_list",db_column="to_user_id")
    from_user=models.ForeignKey(User,related_name='friend_response_list',db_column="from_user_id")

    class Meta:
        unique_together=('to_user','from_user')

    def __unicode__(self):
        return u"%s want to be friend with %s" %(self.from_user.username,self.to_user.username)

class Forum(models.Model):
    title=models.CharField(max_length=200)
    def __unicode__(self):
        return u'Forum: %s' %self.title

    def num_posts(self):
        return sum([t.num_posts() for t in self.thread_set.all()])
    def num_threads(self):
        return self.thread_set.count()

    def last_thread(self):
        if self.thread_set.count():
            return self.thread_set.order_by("-created")[0]
        else: return None

    def last_post(self):
        if self.thread_set.count():
            last = None
            for t in self.thread_set.all():
                l = t.last_post()
                if l:
                    if not last: last = l
                    elif l.created > last.created: last = l
            return last
        else:
            return None

class Thread(models.Model):
    title=models.CharField(max_length=200)
    created=models.DateTimeField(blank=True,auto_now_add=True)
    creator=models.ForeignKey(User,blank=True,null=True)
    forum=models.ForeignKey(Forum)

    def __unicode__(self):
        return u"Thread: %s" %self.title
    def num_posts(self):
        return self.post_set.count()

    def last_post(self):
        if self.post_set.count():
            return self.post_set.order_by("-created")[0]

class Thread_Participant(models.Model):
    thread=models.ForeignKey(Thread,related_name="participant_set",null=True)
    participant=models.ForeignKey(User,related_name="participated_thread_set")
    last_modify=models.DateTimeField(blank=True,null=True)

    def __unicode__(self):
        return u"%s takes part in %s" %(self.participant,self.thread)

class Post(models.Model):
    #title = models.CharField(max_length=60)
    created = models.DateTimeField(blank=True,auto_now_add=True)
    creator = models.ForeignKey(User,blank=True,null=True)
    thread = models.ForeignKey(Thread)
    content = models.TextField(max_length=1000,blank=True)
    link = models.URLField(blank=True)

    def __unicode__(self):
        return u"Post created by %s in %s" % (self.creator.username, self.thread.title)

class Thank(models.Model):
    post=models.ForeignKey(Post)
    to_user=models.ForeignKey(User,related_name="be_thanked_set")
    from_user=models.ForeignKey(User,related_name="has_thanked_set")
    class Meta:
        unique_together=("post","to_user","from_user")