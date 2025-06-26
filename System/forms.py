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


from django import forms
from .models import Quiz, QuestionBank

GROUP_CHOICES = [
    ('ALL', 'All Groups'),
    ('GROUP_A', 'Group A'),  
    ('GROUP_B', 'Group B'),
    ('GROUP_C', 'Group C'),
]

class QuizCreationForm(forms.ModelForm):
    source_type = forms.ChoiceField(
        choices=[
            ('', 'Select Question Bank'),
            ('general', 'General'), 
            ('private', 'Private/Personal'), 
            ('other_staff', "Other Staff")
        ],
        label="Question Bank",
        required=True,
        widget=forms.Select(attrs={
            'id': 'source_bank',
            'name': 'source_bank',
            'class': 'form-control',
            'onchange': 'toggleBankOptions()'
        })
    )
    
    course_code = forms.ChoiceField(
        choices=[
            ('', 'Select Course'),
            ('1', 'Introduction to Computer Science'),
            ('2', 'Data Structures & Algorithms'),
            ('3', 'Web Development'),
            ('4', 'Database Management'),
            ('5', 'Software Engineering'),
        ],
        label="Course",
        required=True,
        widget=forms.Select(attrs={
            'id': 'course',
            'name': 'course',
            'class': 'form-control'
        })
    )
    
    private_bank = forms.ModelChoiceField(
        queryset=QuestionBank.objects.none(), 
        required=False,
        empty_label="Choose your private bank",
        widget=forms.Select(attrs={
            'id': 'private_bank',
            'name': 'private_bank',
            'class': 'form-control'
        })
    )
    
    staff_bank = forms.ModelChoiceField(
        queryset=QuestionBank.objects.none(), 
        required=False,
        empty_label="Choose staff member",
        widget=forms.Select(attrs={
            'id': 'staff_bank',
            'name': 'staff_bank',
            'class': 'form-control'
        })
    )
    
    student_type = forms.ChoiceField(
        choices=[
            ('', 'Select Student Type'),
            ('all', 'All Student Types'),
            ('regular', 'Regular Students'),
            ('evening', 'Evening Students'),
            ('weekend', 'Weekend Students'),
        ],
        label="Student Type",
        required=True,
        widget=forms.Select(attrs={
            'id': 'student_type',
            'name': 'student_type',
            'class': 'form-control'
        })
    )
    
    groups = forms.MultipleChoiceField(
        choices=GROUP_CHOICES, 
        required=False, 
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'checkbox-group'
        })
    )

    class Meta:
        model = Quiz
        fields = [
            'course_code', 'title', 'source_type', 'private_bank', 'staff_bank', 'session',
            'number_of_questions', 'duration_minutes', 'student_type', 'allowed_attempts', 
            'start_time', 'end_time', 'show_results_immediately', 'show_correct_wrong', 
            'randomize_questions', 'randomize_options', 'visibility_to_students', 
            'groups', 'is_open', 'additional_info'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'id': 'title',
                'name': 'title',
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'e.g., Midterm Exam - Chapter 1-5'
            }),
            
            'session': forms.TextInput(attrs={
                'id': 'session',
                'name': 'session',
                'class': 'form-control',
                'maxlength': '20',
                'placeholder': 'e.g., 2024/2025'
            }),
            
            'number_of_questions': forms.NumberInput(attrs={
                'id': 'number_of_questions',
                'name': 'number_of_questions',
                'class': 'form-control',
                'min': '1',
                'max': '100',
                'placeholder': 'e.g., 20'
            }),
            
            'duration_minutes': forms.NumberInput(attrs={
                'id': 'duration_minutes',
                'name': 'duration_minutes',
                'class': 'form-control',
                'min': '1',
                'max': '300',
                'placeholder': 'e.g., 60'
            }),
            
            'allowed_attempts': forms.NumberInput(attrs={
                'id': 'allowed_attempts',
                'name': 'allowed_attempts',
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'value': '1'
            }),
            
            'start_time': forms.DateTimeInput(attrs={
                'id': 'start_time',
                'name': 'start_time',
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            
            'end_time': forms.DateTimeInput(attrs={
                'id': 'end_time',
                'name': 'end_time',
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            
            'additional_info': forms.Textarea(attrs={
                'id': 'additional_info',
                'name': 'additional_info',
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Any special instructions or notes for students...'
            }),
            
            'show_results_immediately': forms.CheckboxInput(attrs={
                'id': 'show_results_immediately',
                'name': 'show_results_immediately',
                'class': 'form-check-input',
                'checked': True
            }),
            
            'show_correct_wrong': forms.CheckboxInput(attrs={
                'id': 'show_correct_wrong',
                'name': 'show_correct_wrong',
                'class': 'form-check-input',
                'checked': True
            }),
            
            'randomize_questions': forms.CheckboxInput(attrs={
                'id': 'randomize_questions',
                'name': 'randomize_questions',
                'class': 'form-check-input',
                'checked': True
            }),
            
            'randomize_options': forms.CheckboxInput(attrs={
                'id': 'randomize_options',
                'name': 'randomize_options',
                'class': 'form-check-input'
            }),
            
            'visibility_to_students': forms.CheckboxInput(attrs={
                'id': 'visibility_to_students',
                'name': 'visibility_to_students',
                'class': 'form-check-input',
                'checked': True
            }),
            
            'is_open': forms.CheckboxInput(attrs={
                'id': 'is_open',
                'name': 'is_open',
                'class': 'form-check-input',
                'checked': True
            }),
        }
        
        labels = {
            'title': 'Quiz Title',
            'session': 'Academic Session',
            'number_of_questions': 'Number of Questions',
            'duration_minutes': 'Duration (Minutes)',
            'allowed_attempts': 'Allowed Attempts',
            'start_time': 'Start Date & Time',
            'end_time': 'End Date & Time',
            'additional_info': 'Additional Instructions',
            'show_results_immediately': 'Show Results Immediately',
            'show_correct_wrong': 'Show Correct/Wrong Answers',
            'randomize_questions': 'Randomize Question Order',
            'randomize_options': 'Randomize Answer Options',
            'visibility_to_students': 'Visible to Students',
            'is_open': 'Quiz is Open',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set up querysets for private and staff banks based on user
        if user:
            self.fields['private_bank'].queryset = QuestionBank.objects.filter(
                created_by=user, is_private=True
            )
            self.fields['staff_bank'].queryset = QuestionBank.objects.filter(
                created_by__is_staff=True
            ).exclude(created_by=user)
        
        # Add help text
        self.fields['number_of_questions'].help_text = "Questions will be randomly selected from the question bank"
        self.fields['allowed_attempts'].help_text = "Number of times a student can take this quiz"
        self.fields['student_type'].help_text = "Choose the type of students this quiz is intended for"
        self.fields['groups'].help_text = "Select which student groups can access this quiz"
        self.fields['additional_info'].help_text = "Optional: Provide any extra information students should know before taking the quiz"