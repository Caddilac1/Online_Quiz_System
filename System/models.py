from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email=email, password=password, username=username, **extra_fields)

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    USERNAME_FIELD = 'username' 
    REQUIRED_FIELDS = ['email','user_type']  

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} - {self.get_user_type_display()}"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# ==============================
# USER PROFILES
# ==============================


LEVEL_CHOICES = [
    ('100', 'Level 100'),
    ('200', 'Level 200'),
    ('300', 'Level 300'),
    ('400', 'Level 400'),
]

GROUP_CHOICES = [
    ('A', 'Group A'),
    ('B', 'Group B'),
    ('C', 'Group C'),
    ('D', 'Group D'),
    ('E', 'Group E'),
    ('F', 'Group F'),
    ('G', 'Group G'),
    ('H', 'Group H'),
    ('I', 'Group I'),
    ('J', 'Group J'),
    ('K', 'Group K'),
    ('L', 'Group L'),
    ('M', 'Group M'),
    ('N', 'Group N'),
    ('O', 'Group O'),
    ('P', 'Group P'),
]

SESSION_CHOICES = [
    ('regular', 'Regular'),
    ('evening', 'Evening'),
    ('weekend', 'Weekend'),
]

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    faculty = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    level = models.CharField(max_length=10, blank=True,choices=LEVEL_CHOICES, default='100')
    group = models.CharField(max_length=5, blank=True,choices=GROUP_CHOICES)
    session = models.CharField(max_length=20, blank=True)
    programme = models.CharField(max_length=100, blank=True)                                                                                                                                                                                                


    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class StaffProfile(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=20, unique=True)
    faculty = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    courses_assigned = models.ManyToManyField('Course', blank=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.staff_id})"


class Semester(models.Model):
    name = models.CharField(max_length=50, unique=True)  
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class AssignedCourse(models.Model):
    staff = models.ForeignKey('StaffProfile', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    semester = models.ForeignKey('Semester', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('staff', 'course', 'semester')  

    def __str__(self):
        return f"{self.staff.user.get_full_name()} → {self.course.code} ({self.semester.name})"


# ==============================
# COURSE MODEL
# ==============================

class Course(models.Model):
    code = models.CharField(max_length=10)
    title = models.CharField(max_length=100)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('code', 'department')

    def __str__(self):
        return f"{self.code} - {self.title} [{self.department.name}]"


# ==============================
# QUESTION BANK (General + Personal)
# ==============================

class QuestionBank(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_general = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        bank_type = "General" if self.is_general else "Personal"
        return f"{self.title} ({bank_type})"


class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')

    def __str__(self):
        return f"{self.name} ({self.faculty.name})"
       

class Question(models.Model):
    bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300, blank=True, null=True) 
    option_d = models.CharField(max_length=300, blank=True, null=True)  
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    tag = models.CharField(max_length=100, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:70] + "..."

# ==============================
# QUIZ SETUP
# ==============================
GROUP_CHOICES = [
    ('Group A', 'Group A'),
    ('Group B', 'Group B'),
    ('Group C', 'Group C'),
    ('Group D', 'Group D'),
    ('Group E', 'Group E'),
    ('Group F', 'Group F'),
    ('Group G', 'Group G'),
    ('Group H', 'Group H'),
    ('Group I', 'Group I'),
    ('Group J', 'Group J'),
    ('Group K', 'Group K'),
    ('Group L', 'Group L'),
    ('Group M', 'Group M'),
    ('Group N', 'Group N'),
    ('Group O', 'Group O'),
    ('Group P', 'Group P'),
]
class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    source_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    number_of_questions = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField()
    allowed_attempts = models.PositiveIntegerField(default=1)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    show_results_immediately = models.BooleanField(default=True)
    show_correct_wrong = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=True)
    randomize_options = models.BooleanField(default=False)
    visibility_to_students = models.BooleanField(default=True)
    session = models.CharField(max_length=20, blank=True)
    groups = models.CharField(max_length=100, blank=True, choices=GROUP_CHOICES) 
    is_open = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('onhold', 'Onhold')
        ],
        default='active'
    )
    additional_info = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.code}"

# ==============================
# STUDENT ATTEMPT & ANSWERS
# ==============================

from django.utils import timezone

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.user.username} - {self.quiz.title}"


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ])
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id} - {self.selected_option}"




class GoogleSheetQuiz(models.Model):
    question_bank = models.ForeignKey(
        'QuestionBank',
        on_delete=models.CASCADE,
        limit_choices_to={'is_general': True}
    )
    sheet_id = models.CharField(max_length=100, blank=True, null=True)
    shared_with = models.ManyToManyField('StaffProfile', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_bank.title} Quiz Sheet"

    def sheet_url(self):
        if self.sheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit"
        return None

    def course(self):
        return self.question_bank.course

    def created_by(self):
        return self.question_bank.created_by


class SheetTask(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(StaffProfile, blank=True)  
    sheet_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.code} - {self.course.title} [{self.course.department.name}]"


class StudentQuizQuestion(models.Model):
    attempt = models.ForeignKey('QuizAttempt', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('attempt', 'question')
