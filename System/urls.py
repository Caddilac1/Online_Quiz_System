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
    path('create-quiz/', create_quiz_view, name='create_quiz'),
    path('get-departments/<int:faculty_id>/', get_departments, name='get_departments'),
    path('resume-quiz/<int:attempt_id>/', resume_quiz_view, name='resume_quiz'),
    path('quiz_instructions/<int:quiz_id>/', quiz_instructions_view, name='quiz_instructions'),
    path('quiz/<int:quiz_id>/start/', start_quiz_view, name='start_quiz'),


]
