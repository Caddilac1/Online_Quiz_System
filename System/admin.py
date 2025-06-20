from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
# === CustomUser Admin ===
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'user_type', 'is_staff', 'is_superuser')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'user_type')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
        )}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'user_type', 'password1', 'password2', 'is_staff', 'is_superuser')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# === StudentProfile Admin ===
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'faculty', 'department', 'level')
    search_fields = ('student_id', 'user__email', 'user__first_name', 'user__last_name')

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'staff_id', 'faculty', 'department', 'is_approved')
    list_filter = ('faculty', 'is_approved')
    search_fields = ('user__email', 'staff_id')
    actions = ['approve_selected']

    @admin.action(description="Approve selected staff")
    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
        
# === Course Admin ===
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title')
    search_fields = ('code', 'title')

# === QuestionBank Admin ===
@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_general', 'created_by', 'created_at')
    list_filter = ('is_general', 'course')
    search_fields = ('title', 'course__code', 'created_by__email')

# === Question Admin ===
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'bank', 'correct_option', 'tag', 'created_at')
    search_fields = ('text', 'tag', 'bank__title')
    list_filter = ('bank__course', 'correct_option')

# === Quiz Admin ===
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_by', 'start_time', 'end_time')
    search_fields = ('title', 'course__code')
    list_filter = ('course', 'start_time', 'end_time')

# === QuizAttempt Admin ===
@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'score', 'submitted_at', 'is_completed')
    list_filter = ('quiz', 'is_completed')
    search_fields = ('quiz__title', 'student__student_id')

# === StudentAnswer Admin ===
@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'is_correct')
    list_filter = ('is_correct', 'selected_option')
    search_fields = ('attempt__student__student_id', 'question__text')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)
    ordering = ('-start_date',)


@admin.register(AssignedCourse)
class AssignedCourseAdmin(admin.ModelAdmin):
    list_display = ('staff', 'course', 'semester')
    list_filter = ('semester', 'staff__department')
    search_fields = (
        'staff__user__first_name', 
        'staff__user__last_name', 
        'course__code', 
        'semester__name'
    )
    autocomplete_fields = ['staff', 'course', 'semester']




