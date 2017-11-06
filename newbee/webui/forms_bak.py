# #coding=utf8
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from newbee.models import *
from django_select2.forms import (
    HeavySelect2MultipleWidget, HeavySelect2Widget, ModelSelect2MultipleWidget,
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)

class BaseSearchFieldMixin(object):
    search_fields = [
        'name__icontains',
        'pk__startswith'
    ]

class BaseModelSelect2MultipleWidget(BaseSearchFieldMixin, ModelSelect2MultipleWidget):
    pass

class BaseModelSelect2Widget(BaseSearchFieldMixin, ModelSelect2Widget):
    pass
#
class LoginForm(AuthenticationForm):
    '''Authentication form which uses boostrap CSS.'''
    username = forms.CharField(max_length=255,widget=forms.TextInput({
                                   'class': 'form-control'}))
    password = forms.CharField(label=_('Password'),
                               widget=forms.PasswordInput({
                                   'class': 'form-control'}))
#




# class MissionForm(forms.ModelForm):
#     version=forms.CharField(label='版本' )
#     remark = forms.CharField(label='备注',required=False)
#
#     def __init__(self, *args, **kwargs):
#         super(MissionForm, self).__init__(*args, **kwargs)
#
#     def clean_version(self):
#         data = self.cleaned_data['version'].strip()
#         return data
#
#     class Meta:
#         model = Mysql_list
#         fields = (
#             'ip',
#             'port',
#             'tag',
#             'deport',
#             'in_charge',
#             'status'
#         )
#         widgets = {
#             'tag': BaseModelSelect2Widget,
#             'in_charge': BaseModelSelect2Widget,
#             'status': BaseModelSelect2Widget,
#         }
