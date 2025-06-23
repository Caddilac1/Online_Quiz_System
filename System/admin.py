from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.utils.html import format_html
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import datetime
from .utils.sheets import create_and_share_sheet, import_questions_from_sheet



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


class QuestionInline(admin.TabularInline):  # Define this FIRST
    model = Question
    extra = 0
    show_change_link = True  # Optional: clickable link to edit question

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):  # Then use it here
    list_display = ('title', 'course', 'is_general', 'created_by', 'created_at')
    search_fields = ('title', 'course__code', 'created_by__username')
    list_filter = ('is_general', 'course')
    inlines = [QuestionInline]

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

from .models import Faculty, Department

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty')
    list_filter = ('faculty',)


SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = settings.GOOGLE_SHEET_CREDENTIALS


@admin.register(GoogleSheetQuiz)
class GoogleSheetQuizAdmin(admin.ModelAdmin):
    list_display = ('question_bank', 'course', 'created_by', 'sheet_link', 'created_at')
    filter_horizontal = ('shared_with',)
    actions = ['create_google_sheet', 'import_questions_from_sheet', 'populate_sample_questions']


    def sheet_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank">Open Sheet</a>' if obj.sheet_id else 'Not created',
            obj.sheet_url()
        )
    sheet_link.short_description = 'Sheet'

    def course(self, obj):
        return obj.question_bank.course

    def created_by(self, obj):
        return obj.question_bank.created_by


    def create_google_sheet(self, request, queryset):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        sheet_service = build('sheets', 'v4', credentials=creds).spreadsheets()
        drive_service = build('drive', 'v3', credentials=creds)

        for quiz in queryset:
            if quiz.sheet_id:
                continue

            title = f"Questions for {quiz.question_bank.course.code} - {quiz.question_bank.title}"
            sheet_body = {
                'properties': {'title': title},
                'sheets': [{
                    'properties': {'title': 'Questions'},
                    'data': [{
                        'startRow': 0,
                        'startColumn': 0,
                        'rowData': [{
                            'values': [{'userEnteredValue': {'stringValue': h}} for h in [
                                'Question Text', 'Option A', 'Option B', 'Option C',
                                'Option D', 'Correct Option', 'Tag']]
                        }]
                    }]
                }]
            }

            sheet_resp = sheet_service.create(body=sheet_body).execute()
            quiz.sheet_id = sheet_resp['spreadsheetId']
            quiz.save()

            # TEMP: Share only with one hardcoded email
            try:
                drive_service.permissions().create(
                    fileId=quiz.sheet_id,
                    body={
                        'type': 'user',
                        'role': 'writer',
                        'emailAddress': 'nabaradirector@gmail.com'
                    },
                    fields='id'
                ).execute()
            except Exception as e:
                self.message_user(request, f"❌ Could not share with nabaradirector@gmail.com: {e}", level='error')


        self.message_user(request, "✅ Sheets created and shared successfully.")

    def import_questions_from_sheet(self, request, queryset):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        spreadsheet_service = build('sheets', 'v4', credentials=creds).spreadsheets()
        values_service = spreadsheet_service.values()

        for quiz in queryset:
            if not quiz.sheet_id:
                self.message_user(request, f"❌ No sheet ID found for {quiz.question_bank.title}.", level='error')
                continue

            try:
                # Get the sheet metadata to compare title
                sheet_info = spreadsheet_service.get(spreadsheetId=quiz.sheet_id).execute()
                actual_title = sheet_info['properties']['title']
                expected_title = quiz.question_bank.course.title.strip().lower()

                # Remove prefix like "Questions for CSSD132 - " before comparing
                if '-' in actual_title:
                    actual_title = actual_title.split('-', 1)[1].strip().lower()
                else:
                    actual_title = actual_title.strip().lower()

                if actual_title != expected_title:
                    self.message_user(
                        request,
                        f"⚠️ Sheet title '{sheet_info['properties']['title']}' does not match course title '{expected_title}'",
                        level='error'
                    )
                    continue


                # Get values from the sheet
                result = values_service.get(
                    spreadsheetId=quiz.sheet_id,
                    range='Questions!A2:G'
                ).execute()

                values = result.get('values', [])
                if not values:
                    self.message_user(request, f"⚠️ No questions found in sheet for {quiz.question_bank.title}", level='warning')
                    continue

                bank = quiz.question_bank

                count = 0
                for row in values:
                    if len(row) < 6:
                        continue
                    try:
                        Question.objects.create(
                            bank=bank,
                            text=row[0],
                            option_a=row[1],
                            option_b=row[2],
                            option_c=row[3],
                            option_d=row[4],
                            correct_option=row[5].strip().upper(),
                            tag=row[6] if len(row) > 6 else ''
                        )
                        count += 1
                    except Exception as e:
                        print(f"⚠️ Failed to import row: {row} | Error: {e}")
                        continue

                self.message_user(request, f"✅ Imported {count} questions into {quiz.question_bank.title}")
            except Exception as e:
                self.message_user(request, f"❌ Error reading from sheet: {e}", level='error')



    def populate_sample_questions(self, request, queryset):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        sheets_api = build('sheets', 'v4', credentials=creds)

        headers = ['Question Text', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Option', 'Tag']

        for quiz in queryset:
            if not quiz.sheet_id:
                self.message_user(request, f"❌ Sheet not created for {quiz.title}.", level='error')
                continue

            questions = []
            for i in range(1, 51):
                questions.append([
                    f"What is question {i}?", f"Option A{i}", f"Option B{i}", f"Option C{i}",
                    f"Option D{i}", "A", f"Tag{i}"
                ])

            body = {
                'values': questions
            }

            sheets_api.spreadsheets().values().append(
                spreadsheetId=quiz.sheet_id,
                range='Questions!A2',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

        self.message_user(request, "✅ 50 sample questions added to each selected sheet.")
                


@admin.register(SheetTask)
class SheetTaskAdmin(admin.ModelAdmin):
    list_display = ('course', 'created_by', 'sheet_url', 'created_at')
    filter_horizontal = ('shared_with',)

    def save_model(self, request, obj, form, change):
        from utils.sheets import create_and_share_sheet
        if not obj.sheet_url:
            title = f"{obj.course.code} - {obj.course.title} Questions"
            emails = ['nabaradirector@gmail.com']  # ✅ Temporary default email
            try:
                obj.sheet_url = create_and_share_sheet(title, emails)
            except Exception as e:
                self.message_user(request, f"❌ Error creating sheet: {e}", level='error')
        super().save_model(request, obj, form, change)
