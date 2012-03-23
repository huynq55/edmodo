import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from library.models import *
from django.forms import ModelForm
from django.utils.safestring import mark_safe

class loginForm(forms.Form):
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
        #widget=forms.FileInput(attrs={'size':80,'margin-right':})
    )

    description=forms.Field(
        widget=forms.Textarea(),
        label='Description',
    )
    '''
    category=forms.ChoiceField(
        choices='Kien,dep,trai',
        label='Category',
    )
    '''
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
    birth_date=forms.DateField()
    email=forms.EmailField(label='Email')
    profile_image=forms.ImageField(
        label="Profile Picture"
    )


FILTER_CHOICES=[
    ('posted_date','Posted Date'),
    ('reading_number','Reading Number'),
    ('like_number','Like Number'),
    ('file_size','File Size'),
]
class FilterForm(forms.Form):
    main_filter=forms.ChoiceField(
        label='',
        choices=FILTER_CHOICES,
    )
    sub_filter=forms.ChoiceField(
        label='',
        choices=[('dec','Decrease'),('inc','Increase')],
    )