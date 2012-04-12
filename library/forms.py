import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from library.models import *
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.forms.widgets import *

class LoginForm(forms.Form):
    username=forms.CharField(label='Username',max_length=200)
    password=forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
    )
class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label='Password (Again)',
        widget=forms.PasswordInput()
    )
    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
        raise forms.ValidationError('Passwords do not match.')
    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Username can only contain alphanumeric characters and the underscore.')
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('Username is already taken.')

class UploadFileForm(forms.Form):
    title=forms.CharField(
        label='Title',max_length=200,
        #widget=forms.TextInput(attrs={'size':80})
    )

    up_file=forms.FileField(
        label='File URL',
    )

    description=forms.Field(
        widget=forms.Textarea(),
        label='Description',
    )
    category=forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='Category',
        initial='',
    )
    public_share=forms.BooleanField(
        initial=False,
        label='Public Sharing',
    )

    title.widget.attrs['size']=50
    up_file.widget.attrs['size']=50
    description.widget.attrs['cols']=50
    #Co the dung text boi doan ma duoc chen vao trong the html
    category.widget.attrs['style']='width:150'


class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
        """Outputs radios"""
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))
GENDER_CHOICES=[('m','Male'),('f','Female')]
class UserInfoForm(forms.Form):
    first_name=forms.CharField(label='First name',max_length=200)
    last_name=forms.CharField(label='Last name',max_length=200)
    gender=forms.ChoiceField(
        label='Gender',
        widget=forms.RadioSelect(renderer=HorizRadioRenderer),
        choices=GENDER_CHOICES,
        initial='m',
    )
    email=forms.EmailField(label='Email')
    about=forms.CharField(label='About',max_length=500,widget=forms.Textarea)

class ProfileImageChangeForm(forms.Form):
    profile_image=forms.ImageField(
        label="Profile Picture",
        required=False
    )

class PasswordChangeForm(forms.Form):
    old_password=forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(),
    )
    new_password1=forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(),
    )
    new_password2=forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(),
    )
    def clean_new_password2(self):
        if 'password1' in self.cleaned_data:
            new_password1 = self.cleaned_data['new_password1']
            new_password2 = self.cleaned_data['new_password2']
            if new_password1 == new_password2:
                return new_password2
        raise forms.ValidationError('Passwords do not match.')

MAIN_FILTER_CHOICES=[
    ('posted_date','Posted Date'),
    ('reading_number','Reading Number'),
    ('like_number','Like Number'),
    ('file_size','File Size'),
]
SUB_FILTER_CHOICES=[('dec','Decrease'),('inc','Increase')]
class FilterForm(forms.Form):
    main_filter=forms.ChoiceField(
        label='',
        choices=MAIN_FILTER_CHOICES,
    )
    sub_filter=forms.ChoiceField(
        label='',
        choices=SUB_FILTER_CHOICES,
    )

class ReplyForm(forms.Form):
    content=forms.CharField(
        max_length=1000,
        label='Content',
        widget=forms.Textarea(),
        required=False,
    )
    attach_link=forms.URLField(
        label='Attach Link',
        required=False,
    )
class NewThreadForm(forms.Form):
    subject=forms.CharField(
        max_length=200,
        label='Subject',
    )

class AddVideoForm(forms.Form):
    url=forms.URLField(
        max_length=300,
        label='URL',
    )
    description=forms.Field(
        widget=forms.Textarea(),
        label='Description',
    )
    public_share=forms.BooleanField(
        initial=False,
        label='Public Sharing',
    )

    url.widget.attrs['size']=54
    url.widget.attrs['value']="http://"


class UploadImageForm(forms.Form):
    up_file=forms.ImageField(
        label='Image URL',
    )

    description=forms.Field(
        widget=forms.Textarea(),
        label='Description',
    )
    public_share=forms.BooleanField(
        initial=False,
        label='Public Sharing',
    )
    up_file.widget.attrs['size']=55
    description.widget.attrs['cols']=50

class AddImageLinkForm(forms.Form):
    url=forms.URLField(
        max_length=300,
        label='URL',
    )
    description=forms.Field(
        widget=forms.Textarea(),
        label='Description',
    )
    public_share=forms.BooleanField(
        initial=False,
        label='Public Sharing',
    )

    url.widget.attrs['size']=54
    url.widget.attrs['value']="http://"

