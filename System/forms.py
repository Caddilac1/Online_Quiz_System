from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'title']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS101'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Title'}),
        }


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, StaffProfile, Faculty, Department

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, StaffProfile, Faculty, Department

class DepartmentAdminCreationForm(UserCreationForm):
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'faculty'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'department'})
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password1', 'password2', 'faculty', 'department']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
