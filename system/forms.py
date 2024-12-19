from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )


class SignUpForm(UserCreationForm):


    class Meta:
        model = User
        fields = [ 'username', 'email', 'password1', 'password2']


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'availability', 'category_id']

    category_id = forms.ModelChoiceField(
    queryset=Category.objects.all(),
    empty_label="Select Category",
    widget=forms.Select(attrs={'class': 'form-control'}),
    label='Category',
   )
    
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['educator', 'service', 'day', 'time_start', 'time_end']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['educator'].queryset = User.objects.filter(is_educator=True)
        self.fields['service'].queryset = Service.objects.all()


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['client', 'educator', 'schedule']


class TherapistAssignmentForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'assigned_therapist']
        widgets = {
            'assigned_therapist': forms.Select(attrs={'class': 'form-control'}),
        }
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category']  # Include fields you want to add/edit
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
        }
        labels = {
            'category': 'Category Name',
        }