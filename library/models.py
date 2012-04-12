from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import os
from easy_thumbnails.models import Thumbnail
from easy_thumbnails import fields
# Create your models here.

def dynamic_upload(instance, filename):
    type=''
    username=''
    if instance.__class__=='Book':
        type='books'
        username=instance.uploader.username
    if instance.__class__=='Lib_Image':
        type='images'
        username=instance.uploader.username
    if instance.__class__=='User_Information':
        type='profile_imgs'
        username=instance.user.username
    if type :
        return '/'.join([username,type, filename])
    else :
        return '/'.join([username, filename])

class Category(models.Model):
    name=models.CharField(max_length=200)
    def __str__(self):
        return '%s' %self.name

class Book(models.Model):
    title=models.CharField(max_length=200)
    category=models.ForeignKey(Category)
    file=models.FileField(upload_to=dynamic_upload,blank=True)
    thumbnail=fields.ThumbnailerField(upload_to='thumbnail',blank=True)
    uploader=models.ForeignKey(User,related_name='book_list')
    description=models.TextField(blank=True)
    upload_date=models.DateTimeField(auto_now_add=True)
    public_share=models.BooleanField(default=False)
    read_count=models.IntegerField(default=0)
    def __str__(self):
        return '%s,%s' %(self.title,self.uploader)
    def num_downloader(self):
        return self.downloader_set.count()
    def num_reader(self):
        return self.reader_set.count()
    def num_voter(self):
        return self.vote_set.count()
    def book_size(self):
        if self.file :
            return self.file.size
        else: return 0
class Image(models.Model):
    image_file=models.ImageField(upload_to=dynamic_upload,blank=True)
    uploader=models.ForeignKey(User,related_name='image_list')
    description=models.TextField(blank=True)
    upload_date=models.DateTimeField(auto_now_add=True)
    public_share=models.BooleanField(default=False)

class Video(models.Model):
    uploader=models.ForeignKey(User,related_name='video_list')
    description=models.TextField(blank=True)
    upload_date=models.DateTimeField(auto_now_add=True)
    public_share=models.BooleanField(default=False)

class User_Information(models.Model):
    user=models.OneToOneField(User)
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    gender=models.IntegerField(max_length=1,default=1)
    image=models.ImageField(upload_to='kien',blank=True,null=True)
    visiting_number=models.IntegerField(default=0,max_length=5,editable=False)
    read_books=models.ManyToManyField(Book,related_name='reader_set',editable=False)
    downloaded_books=models.ManyToManyField(Book,related_name='downloader_set',editable=False)
    def __str__(self):
        return '%s %s' %(self.first_name,self.last_name)


class Vote(models.Model):
    book=models.ForeignKey(Book)
    voter=models.ForeignKey(User)
    vote_date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return 'Vote for: %s from %s' %(self.book.title,self.voter.username)

class Friend(models.Model):
    host=models.ForeignKey(User,related_name='friend_list')
    friend_id=models.IntegerField(max_length=4)

class Forum(models.Model):
    title=models.CharField(max_length=200)
    def __unicode__(self):
        return self.title
    def num_posts(self):
        return sum([t.num_posts() for t in self.thread_set.all()])
    def num_threads(self):
        return self.thread_set.count()
    def last_post(self):
        if self.thread_set.count():
            last = None
            for t in self.thread_set.all():
                l = t.last_post()
                if l:
                    if not last: last = l
                    elif l.created > last.created: last = l
            return last


class Thread(models.Model):
    title=models.CharField(max_length=200)
    created=models.DateTimeField(auto_now_add=True)
    creator=models.ForeignKey(User,blank=True,null=True)
    forum=models.ForeignKey(Forum)
    notification=models.IntegerField(default=0)
    def __unicode__(self):
        return unicode(self.creator) + " - " + self.title
    def num_posts(self):
        return self.post_set.count()

    def num_replies(self):
        reply_number=0
        for post in self.post_set.all():
            if post.creator is not self.creator:
                reply_number+=1
        return reply_number

    def last_post(self):
        if self.post_set.count():
            return self.post_set.order_by("created")[0]

class Post(models.Model):
    #title = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User,blank=True,null=True)
    thread = models.ForeignKey(Thread)
    content = models.TextField(max_length=1000,blank=True)
    link = models.URLField(blank=True)

    def __unicode__(self):
        return u"%s - %s" % (self.creator, self.thread)

    def short(self):
        return u"%s\n%s" % (self.creator, self.created.strftime("%b %d, %I:%M %p"))
    short.allow_tags = True
