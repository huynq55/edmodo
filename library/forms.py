import re
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from library.models import *
from django.utils.safestring import mark_safe

class LoginForm(forms.Form):
    username=forms.CharField(label='Username',max_length=200)
    password=forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
    )
class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=200)
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
        if 'new_password1' in self.cleaned_data:
            new_password1 = self.cleaned_data['new_password1']
            new_password2 = self.cleaned_data['new_password2']
            if new_password1 == new_password2:
                return new_password2
        raise forms.ValidationError('New passwords do not match.')


class UploadBookForm(forms.Form):
    title=forms.CharField(
        label='Title',max_length=200,
        widget=forms.TextInput(attrs={'size':50,})
    )
    up_file=forms.FileField(label='Book URL',)
    description=forms.Field(
        widget=forms.Textarea(attrs={'cols':50,}),
        label='Description',
        required=False,
    )
    public_share=forms.BooleanField(
        initial=False,required=False,
        label='Public Sharing',
    )

class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
        """Outputs radios"""
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

GENDER_CHOICES=[('m','Male'),('f','Female')]
class UserInfoForm(forms.Form):
    first_name=forms.CharField(label='First name',max_length=200,required=False,)
    last_name=forms.CharField(label='Last name',max_length=200,required=False,)
    gender=forms.ChoiceField(
        label='Gender',
        widget=forms.RadioSelect(renderer=HorizRadioRenderer),
        choices=GENDER_CHOICES,
        required=False,
    )
    day=forms.ChoiceField(
        label='Day',
        choices=((str(x), x) for x in range(1,32)),
        required=False,
    )
    month=forms.ChoiceField(
        label='Month',
        choices=((str(x), x) for x in range(1,13)),
        required=False,
    )
    year=forms.ChoiceField(
        label='Year',
        choices=((str(x), x) for x in range(1900,2013)),
        required=False,
    )
    about=forms.CharField(
        label='About',max_length=500,
        widget=forms.Textarea(attrs={'placeholder':"Write some notes about yourself",'style':'width:400px;height:150px'}),
        required=False,
    )
    day.widget.attrs['style']='width:80px'
    month.widget.attrs['style']='width:80px'
    year.widget.attrs['style']='width:80px'

class ProfileImageChangeForm(forms.Form):
    profile_image=forms.ImageField(
        label="Profile Picture",
    )


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

class NewPostForm(forms.Form):
    content=forms.CharField(
        max_length=1000,
        label='Content',
        widget=forms.Textarea(attrs={'style':'min-width:400px'}),
        required=False,
    )
    attach_link=forms.URLField(
        label='Attach Link',
        required=False,
    )
    attach_link.widget.attrs['style']='min-width:400px'
class NewThreadForm(forms.Form):
    subject=forms.CharField(
        max_length=200,
        label='Subject',
    )


class UploadVideoLinkForm(forms.Form):
    title=forms.CharField(label='Title',max_length=200)
    link=forms.URLField(
        label='Video Link',
        widget=forms.TextInput(attrs={'placeholder':"http://",})
    )
    description=forms.Field(
        widget=forms.Textarea(attrs={'cols':50,}),
        label='Description',
        required=False,
    )
    public_share=forms.BooleanField(
        initial=False, required=False,
        label='Public Sharing',
    )

class UploadImageForm(forms.Form):
    title=forms.CharField(label='Title',max_length=200)
    up_file=forms.ImageField(
        label='Image URL',
    )
    description=forms.Field(
        widget=forms.Textarea(attrs={'cols':50,}),
        label='Description',
        required=False
    )
    public_share=forms.BooleanField(
        initial=False, required=False,
        label='Public Sharing',
    )

class UploadImageLinkForm(forms.Form):
    title=forms.CharField(label='Title',max_length=200)
    link=forms.URLField(
        label='Image Link',
        widget=forms.TextInput(attrs={'placeholder':"http://",})
    )
    description=forms.Field(
        widget=forms.Textarea(attrs={'cols':50,}),
        label='Description',
        required=False,
    )
    public_share=forms.BooleanField(
        initial=False, required=False,
        label='Public Sharing',
    )

class SearchForm(forms.Form):
    query=forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'size':50,'placeholder':'Please enter a keyword to search'})
    )
    book_search=forms.BooleanField(
        label='Books',
        widget=forms.CheckboxInput(),
        initial=False,required=False,
    )
    image_search=forms.BooleanField(
        label='Images',
        widget=forms.CheckboxInput(),
        initial=False,required=False,
    )
    video_search=forms.BooleanField(
        label='Videos',
        widget=forms.CheckboxInput(),
        initial=False,required=False,

    )