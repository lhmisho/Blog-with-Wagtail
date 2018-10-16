from django import forms
from dit_email_addon.api import DitEmailAddon
from django.conf import settings
from crispy_forms.helper import Layout, FormHelper
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import Div
from django.contrib import messages
from wagtailhyper.forms import HyperForm
import threading

def send_email_async(data):
    contact_email = getattr(settings, 'CONTACT_EMAIL', 'shimul@divine-it.net')
    DitEmailAddon().send_email_default(contact_email, 'contact', data)
    DitEmailAddon().send_email_default(data['email'], 'contact_reply', data)

class ContactForm(HyperForm):
    name = forms.CharField(max_length=255, label='', widget=forms.TextInput(attrs={'placeholder': 'Name'}) )
    company_name = forms.CharField(max_length=255, required=False, label='', widget=forms.TextInput(attrs={'placeholder': 'Company Name'}) )
    phone = forms.CharField(max_length=25, label='', widget=forms.TextInput(attrs={'placeholder': 'Phone'}) )
    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    country = forms.CharField(max_length=20, required=False,  label='', widget=forms.TextInput(attrs={'placeholder': 'Country'}))
    message = forms.CharField(required=False, label='', widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write Your Requirement'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div('name'),
            Div('company_name'),
            Div(
                Div('phone', css_class='col-6'),
                Div('email', css_class='col-6'),
                css_class='row'
            ),
            Div('country'),
            Div('message'),
            Div(
                Submit('Submit', 'Submit', css_class='btn btn-outline-primary'),
                css_class='form-action-wrap text-center'
            )
        )

    def is_valid(self):
        if super().is_valid():
            threading.Thread(target=send_email_async, args=[self.data]).start()
            messages.success(self.request, 'Your message has been sent successfully.')
            return True
        else:
            return False
