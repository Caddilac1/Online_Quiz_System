from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('', register_student, name='register_student'),
    path('register_staff/', register_staff, name='register_staff'),
    path('login', login_view, name='login'),
    path('student_dashboard/', student_dashboard, name='student_dashboard'),
    path('staff_dashboard/', staff_dashboard, name='staff_dashboard'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    path('add-course/', add_course, name='add_course'),
    path('create-department-admin/', create_department_admin, name='create_department_admin'),
]
