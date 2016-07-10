from django import forms
from django.core import validators

class MantisField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(MantisField, self).__init__(*args, **kwargs)
        self.validators.append(validators.RegexValidator(
            regex = r'^[\d\n\r, ]*$',
            message = 'Please enter only numbers, separated by commas, newlines or spaces.',
        ))

class RegisterForm(forms.Form):
    username = forms.CharField(label='Username*')
    email = forms.EmailField(label='E-Mail*')
    firstname = forms.CharField(label='First name', required=False)
    lastname = forms.CharField(label='Last name', required=False)
    password = forms.CharField(label='Password*', widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label='Password (again)*', widget=forms.PasswordInput(render_value=False))

class ProjectForm(forms.Form):
    name = forms.CharField(label='Project-Nr')
    desc = forms.CharField(label='Name', required=False)

class BoardClassForm(forms.Form):
    name = forms.CharField(label='Name')
    desc = forms.CharField(label='Description', required=False, widget=forms.Textarea())
    productnr = forms.CharField(label='Product-ID')
    revision = forms.CharField(label='Revision', required=False)

class BoardForm(forms.Form):
    csnr = forms.CharField(label='Internal ID')
    comment = forms.CharField(label='Comment', widget=forms.Textarea(), required=False)
    serial_top = forms.CharField(label='Top serial', required=False)
    serial_bottom = forms.CharField(label='Bottom serial', required=False)
    defect = forms.BooleanField(label='Defect?', required=False)
    swversion = forms.CharField(label='SW version', required=False)
    attachment = forms.FileField(widget=forms.FileInput(), required=False)

class PatchForm(forms.Form):
    name = forms.CharField(max_length=30)
    desc = forms.CharField(max_length=2000, widget=forms.Textarea(), required=False)
    why = forms.CharField(max_length=2000, widget=forms.Textarea(), required=False)
    mandatory = forms.NullBooleanField('Mandatory')
    mantis = MantisField(max_length=2000, widget=forms.Textarea(), required=False)
    attachment = forms.FileField(widget=forms.FileInput(), required=False)

class EventForm(forms.Form):
    desc = forms.CharField(max_length=2000, widget=forms.Textarea(), required=True, label="Description")

class LocationForm(forms.Form):
    location = forms.CharField(max_length=200, required=True, label="Location")

class SearchForm(forms.Form):
    searchstring = forms.CharField(max_length=200, required=True, label="Search-pattern")
    search_boardname = forms.BooleanField(label="Search boardname?", initial=True)
    search_projectname = forms.BooleanField(label="Search projectname?", initial=True)
    search_serial = forms.BooleanField(label="Search serial numbers?", initial=True)
    search_productnr = forms.BooleanField(label="Search product-nr?", initial=True)
    search_patchnr = forms.BooleanField(label="Search patch-nr?", initial=True)
