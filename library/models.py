from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import os
from easy_thumbnails.models import Thumbnail
from easy_thumbnails import fields
# Create your models here.
def get_CategoryFolder(category_name):
    if category_name is None:
        return 'book/'
    else:
        return os.path.join('book/',category_name)
class Category(models.Model):
    name=models.CharField(max_length=200)
    def __str__(self):
        return '%s' %self.name

class Book(models.Model):
    title=models.CharField(max_length=200)
    category=models.ForeignKey(Category)
    file=models.FileField(upload_to=get_CategoryFolder(category.name),blank=True)
    thumbnail=fields.ThumbnailerField(upload_to='thumbnail',blank=True)
    uploader=models.ForeignKey(User,related_name='book_list')
    description=models.TextField(blank=True)
    upload_date=models.DateTimeField(auto_now_add=True)
    public_share=models.BooleanField(default=False)
    read_count=models.IntegerField(default=0)
    def get_uploadFolder(self):
        return os.path.join('book/',self.category.name)
    def __str__(self):
        return '%s,%s' %(self.title,self.uploader)

class User_Information(models.Model):
    user=models.OneToOneField(User)
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    gender=models.IntegerField(max_length=1,default=1)
    image=models.ImageField(upload_to='user_images',blank=True)
    visiting_number=models.IntegerField(max_length=5,editable=False)
    read_books=models.ManyToManyField(Book,related_name='reader_set',editable=False)
    downloaded_books=models.ManyToManyField(Book,related_name='downloader_set',editable=False)
    def __str__(self):
        return '%s,%s' %(self.first_name,self.last_name)


class Vote(models.Model):
    book=models.ForeignKey(Book)
    voter=models.ForeignKey(User)
    vote_date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return 'Vote for: %s from %s' %(self.book.title,self.voter.username)

class Friend(models.Model):
    host=models.ForeignKey(User,related_name='friend_list')
    friend_id=models.IntegerField(max_length=4)