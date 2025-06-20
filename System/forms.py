from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, StudentProfile, StaffProfile

class StudentRegistrationForm(UserCreationForm):
    student_id = forms.CharField(max_length=20)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        user.username = ''  
        user.save()
        StudentProfile.objects.create(
            user=user,
            student_id=self.cleaned_data['student_id']
        )
        return user

class StaffRegistrationForm(UserCreationForm):
    staff_id = forms.CharField(max_length=20)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'staff'
        user.username = ''
        user.save()
        StaffProfile.objects.create(
            user=user,
            staff_id=self.cleaned_data['staff_id']
        )
        return user
