from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, StudentProfile, StaffProfile, Semester, Course,
    AssignedCourse, QuestionBank, Question, Quiz, QuizAttempt, StudentAnswer
)

# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('user_type', 'profile_picture')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'user_type', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'faculty', 'department', 'level', 'group', 'session')
    search_fields = ('student_id', 'user__username', 'user__email')
    list_filter = ('faculty', 'department', 'level', 'session')


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'staff_id', 'faculty', 'department', 'position', 'is_verified', 'is_approved')
    search_fields = ('staff_id', 'user__username', 'user__email')
    list_filter = ('faculty', 'department', 'is_verified', 'is_approved')


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title')
    search_fields = ('code', 'title')


@admin.register(AssignedCourse)
class AssignedCourseAdmin(admin.ModelAdmin):
    list_display = ('staff', 'course', 'semester')
    search_fields = ('staff__user__username', 'course__code')
    list_filter = ('semester',)


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_general', 'created_by', 'created_at')
    search_fields = ('title', 'course__code', 'created_by__username')
    list_filter = ('is_general', 'course')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('bank', 'text', 'tag', 'created_at')
    search_fields = ('text', 'tag')
    list_filter = ('bank',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_by', 'start_time', 'end_time', 'is_open')
    search_fields = ('title', 'course__code', 'created_by__username')
    list_filter = ('course', 'is_open', 'start_time', 'end_time')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'score', 'submitted_at', 'is_completed')
    search_fields = ('quiz__title', 'student__user__username')
    list_filter = ('quiz', 'is_completed')


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'is_correct')
    search_fields = ('attempt__student__user__username', 'question__text')
    list_filter = ('is_correct',)

