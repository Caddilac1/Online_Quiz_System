from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from .utils.sheets import create_and_share_sheet, import_questions_from_sheet
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.contrib import messages
from .models import *
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.http import JsonResponse
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404



def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = request.build_absolute_uri(f"/activate/{uid}/{token}/")

    subject = 'Activate Your Account - GCTU Online Exams System'

    # HTML version
    html_message = render_to_string('email_template.html', {
        'user': user,
        'activation_link': activation_link,
    })

    # Plaintext fallback (optional but good practice)
    text_message = f"""
Hello {user.get_full_name()},

Welcome to the GCTU Online Quiz & Exams System.

To activate your account, visit this link:
{activation_link}

If you didn't request this, you can ignore this email.
"""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_message, "text/html")
    email.send()


def register_student(request):
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    if request.method == 'POST':
        full_name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        index_number = request.POST.get('index-number', '').strip()
        faculty_id = request.POST.get('faculty')
        department_id = request.POST.get('department')
        programme = request.POST.get('programme')
        level = request.POST.get('level')
        session = request.POST.get('session')


        # === Basic Server-side Validation ===
        errors = []

        if not full_name:
            errors.append("Full name is required.")
        if not email:
            errors.append("Email is required.")
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        # === Check if email or index already exists ===
        if CustomUser.objects.filter(email=email).exists():
            errors.append("An account with this email already exists.")
        if StudentProfile.objects.filter(student_id=index_number).exists():
            errors.append("This index number is already registered.")


        try:
            faculty_instance = Faculty.objects.get(id=faculty_id)
        except Faculty.DoesNotExist:
            errors.append("Selected faculty does not exist.")

        try:
            department_instance = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            errors.append("Selected department does not exist.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'student_signup.html',{'faculties': faculties, 'departments': departments})

        # === Split full name ===
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # === Create User (inactive) ===
        user = CustomUser.objects.create(
            email=email,
            username=index_number,  
            first_name=first_name,
            last_name=last_name,
            user_type='student',
            password=make_password(password),
            is_active=False  
        )

        # === Create Student Profile ===
        StudentProfile.objects.create(
            user=user,
            student_id=index_number,
            faculty=faculty_instance,
            programme=programme,
            department=department_instance,
            level=level,
            session=session
        )

        # === Send Email Verification ===
        send_verification_email(user, request)
        return render(request, 'email_sent.html', {'user': user})


        messages.success(request, "Account created! Please check your email to verify your account.")
        return redirect('login')

    return render(request, 'student_signup.html', {'faculties': faculties, 'departments': departments})

def register_staff(request):
    faculties = Faculty.objects.all()
    departments = Department.objects.all()

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        staff_id = request.POST.get('staff_id', '').strip()
        faculty_id = request.POST.get('faculty')
        department_id = request.POST.get('department')
        position = request.POST.get('position')
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        errors = []

        # ===== VALIDATION =====
        if not full_name:
            errors.append("Full name is required.")
        if not staff_id:
            errors.append("Staff ID is required.")
        if not email or '@' not in email:
            errors.append("A valid email is required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if CustomUser.objects.filter(email=email).exists():
            errors.append("An account with this email already exists.")
        if StaffProfile.objects.filter(staff_id=staff_id).exists():
            errors.append("This staff ID is already registered.")

        # Fetch foreign key instances
        try:
            faculty = Faculty.objects.get(id=faculty_id)
        except Faculty.DoesNotExist:
            errors.append("Invalid faculty selected.")

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            errors.append("Invalid department selected.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'staff_signup.html', {
                'faculties': faculties,
                'departments': departments
            })

        # ===== CREATE USER =====
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        user = CustomUser.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type='staff',
            is_active=False, 
            password=make_password(password)
        )

        # ===== CREATE PROFILE =====
        StaffProfile.objects.create(
            user=user,
            staff_id=staff_id,
            faculty=faculty,
            department=department,
            position=position
        )

        send_staff_activation_email(user, request)
        notify_admin_of_staff_registration(user, staff_id)

        return render(request, 'email_sent.html', {'user': user})

    return render(request, 'staff_signup.html', {'faculties': faculties, 'departments': departments})

def send_staff_activation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = request.build_absolute_uri(f"/activate/{uid}/{token}/")

    subject = 'Activate Your Account - GCTU Online Exams System'

    html_message = render_to_string('email_template.html', {
        'user': user,
        'activation_link': activation_link,
    })

    text_message = f"""
Hello {user.get_full_name()},

Thank you for registering for the GCTU Online Exams System.

Please activate your account using the link below:
{activation_link}

If you didn’t sign up, you can safely ignore this email.
"""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_message, "text/html")
    email.send()


def notify_admin_of_staff_registration(user, staff_id):
    subject = "New Staff Registration - GCTU Exams System"
    
    html_message = render_to_string('notify_admin.html', {
        'full_name': user.get_full_name(),
        'staff_id': staff_id,
        'email': user.email,
        'faculty': user.staffprofile.faculty,
        'department': user.staffprofile.department,
        'position': user.staffprofile.position,
        'site_name': "GCTU Exams System",
    })

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [settings.ADMIN_EMAIL]

    email = EmailMultiAlternatives(subject, '', from_email, to_email)
    email.attach_alternative(html_message, "text/html")
    email.send()


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        
        if user.user_type == 'staff' and hasattr(user, 'staffprofile'):
            staff_profile = user.staffprofile
            if not staff_profile.is_approved:
                return render(request, 'pending_approval.html') 

        return render(request, 'email_verified.html')  

    return render(request, 'activation_failed.html')

def login_view(request):
    if request.method == "POST":
        input_value = request.POST.get("username").strip()
        password = request.POST.get("password")

        print("🔍 Login attempt")
        print(f"👉 Input: {input_value}")
        print(f"👉 Password provided: {'Yes' if password else 'No'}")

        user = None

        # Try to find user by email (staff login)
        try:
            user = CustomUser.objects.get(email=input_value)
            print("✅ Found user by email:", user)
        except CustomUser.DoesNotExist:
            print("❌ No user found with that email")

        # Try to find user by student index number (student login)
        if user is None:
            try:
                student_profile = StudentProfile.objects.get(student_id=input_value)
                user = student_profile.user
                print("✅ Found student user by index number:", user)
            except StudentProfile.DoesNotExist:
                print("❌ No student found with index number:", input_value)

        # Attempt authentication
        if user:
            username = user.username or user.email
            print("🔐 Authenticating with username:", username)
            user = authenticate(request, username=username, password=password)
        else:
            print("❗ No user object to authenticate")

        if user is not None:
            print("✅ Authentication successful")

            if not user.is_active:
                print("⚠️ Account is inactive")
                messages.error(request, "Your account is inactive. Please check your email for the activation link.")
                return render(request, "login.html")

            # ✅ Check staff approval before login
            if hasattr(user, 'staffprofile') and not user.staffprofile.is_approved:
                print("❌ Staff account not yet approved by admin")
                messages.error(request, "Your account is pending approval by the administrator.")
                return render(request, "login.html")

            login(request, user)
            print("✅ User logged in:", user.email)

            if hasattr(user, 'studentprofile'):
                print("🔀 Redirecting to student dashboard")
                return redirect('student_dashboard')

            elif hasattr(user, 'staffprofile'):
                print("🔀 Redirecting to staff dashboard")
                return redirect('staff_dashboard')

            elif user.is_superuser:
                print("🔀 Redirecting to admin dashboard")
                return redirect('/admin/')

            else:
                print("❓ No profile linked to user")
                messages.warning(request, "Login successful but your account has no profile linked.")
                return redirect('login')
        else:
            print("❌ Authentication failed")
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, "login.html")


@login_required
def student_dashboard(request):
    now = timezone.now()
    upcoming_quizzes = Quiz.objects.filter(
        is_open=True,
        visibility_to_students=True,
        start_time__gt=now
    ).order_by('start_time')  # Order so the soonest quiz is first

    quizzes = []
    announcement_quiz = None

    for quiz in upcoming_quizzes:
        time_left = quiz.start_time - now
        urgent = time_left.total_seconds() <= 7200  

        quiz_dict = {
            'id': quiz.id,
            'course_code': quiz.course.code,
            'title': quiz.title,
            'time_left': time_left,
            'urgent': urgent,
            'start_time': quiz.start_time,
        }

        quizzes.append(quiz_dict)

    
    if quizzes:
        announcement_quiz = quizzes[0]

    return render(request, 'student_dashboard.html', {
        'quizzes': quizzes,
        'announcement_quiz': announcement_quiz,
    })

@login_required
def staff_dashboard(request):
    quizes = Quiz.objects.filter(created_by=request.user)
    if hasattr(request.user, 'staffprofile'):
        return render(request, 'staff_dashboard.html', {'staff': request.user.staffprofile , 'quizzes': quizes})
    return redirect('login')


@login_required
def add_course(request):
    if not (request.user.is_superuser or request.user.user_type == 'admin'):
        return redirect('login')  

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_course')  
    else:
        form = CourseForm()

    courses = Course.objects.all()
    return render(request, 'add_course.html', {'form': form, 'courses': courses})    


@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin')
def create_department_admin(request):
    if request.method == 'POST':
        form = DepartmentAdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'staff'
            user.save()

            StaffProfile.objects.create(
                user=user,
                faculty=form.cleaned_data['faculty'],
                department=form.cleaned_data['department'],
                position="Department Admin",
                is_verified=True,
                is_approved=True
            )

            messages.success(request, "Department Admin created successfully!")
            return redirect('create_department_admin')
    else:
        form = DepartmentAdminCreationForm()

    return render(request, 'create_department_admin.html', {'form': form})



def create_quiz_view(request):
    if request.method == 'POST':
        print("📥 POST request received for creating quiz.")

        course_code = request.POST.get('course', '').strip().upper()
        print(f"🔍 Course code received: {course_code}")

        title = request.POST.get('title', '').strip()
        print(f"📚 Quiz title: {title}")

        source_type = request.POST.get('source_bank')
        print(f"🗃️ Source bank type: {source_type}")

        session = request.POST.get('session')
        additional_info = request.POST.get('additional_info', '')
        number_of_questions = request.POST.get('number_of_questions')
        duration_minutes = request.POST.get('duration_minutes')
        allowed_attempts = request.POST.get('allowed_attempts')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        show_results_immediately = 'show_results_immediately' in request.POST
        show_correct_wrong = 'show_correct_wrong' in request.POST
        randomize_questions = 'randomize_questions' in request.POST
        randomize_options = 'randomize_options' in request.POST
        visibility_to_students = 'visibility_to_students' in request.POST
        is_open = 'is_open' in request.POST

        selected_groups = request.POST.getlist('groups')
        print(f"👥 Selected groups: {selected_groups}")
        group_string = ",".join(selected_groups)

        try:
            course = Course.objects.get(code=course_code)
            print("✅ Course found in database.")
        except Course.DoesNotExist:
            print("❌ Course not found!")
            messages.error(request, "❌ Course with code not found.")
            return render(request, 'staff_create_quiz.html')

        # Resolve the correct question bank
        if source_type == 'general':
            try:
                bank = QuestionBank.objects.get(course=course, is_general=True)
                print("✅ General bank found.")
            except QuestionBank.DoesNotExist:
                print("❌ No general bank found.")
                messages.error(request, "❌ No general bank found for this course.")
                return render(request, 'staff_create_quiz.html')
        elif source_type == 'private':
            private_bank_id = request.POST.get('private_bank')
            print(f"🔐 Private bank ID: {private_bank_id}")
            try:
                bank = QuestionBank.objects.get(id=private_bank_id, created_by=request.user, is_general=False)
                print("✅ Private bank found.")
            except QuestionBank.DoesNotExist:
                print("❌ Private bank not found.")
                messages.error(request, "❌ Selected private bank not found.")
                return render(request, 'staff_create_quiz.html')
        elif source_type == 'other_staff':
            staff_bank_id = request.POST.get('staff_bank')
            print(f"👤 Staff bank ID: {staff_bank_id}")
            try:
                bank = QuestionBank.objects.get(id=staff_bank_id, is_general=False)
                print("✅ Other staff bank found.")
            except QuestionBank.DoesNotExist:
                print("❌ Other staff bank not found.")
                messages.error(request, "❌ Selected staff bank not found.")
                return render(request, 'staff_create_quiz.html')
        else:
            print("❌ Invalid bank type.")
            messages.error(request, "❌ Invalid question bank type selected.")
            return render(request, 'staff_create_quiz.html')

        # Create and save the quiz
        print("💾 Creating quiz object...")
        quiz = Quiz(
            title=title,
            course=course,
            source_bank=bank,
            session=session,
            additional_info=additional_info,
            number_of_questions=number_of_questions,
            duration_minutes=duration_minutes,
            allowed_attempts=allowed_attempts,
            start_time=start_time,
            end_time=end_time,
            show_results_immediately=show_results_immediately,
            show_correct_wrong=show_correct_wrong,
            randomize_questions=randomize_questions,
            randomize_options=randomize_options,
            visibility_to_students=visibility_to_students,
            is_open=is_open,
            created_by=request.user,
            groups=group_string
        )
        quiz.save()
        print(f"✅ Quiz saved with ID: {quiz.id}")

        messages.success(request, "✅ Quiz created successfully.")
        return redirect('staff_dashboard')

    # GET request
    print("🌐 GET request received - rendering quiz creation form.")
    private_banks = QuestionBank.objects.filter(created_by=request.user, is_general=False)
    staff_banks = QuestionBank.objects.exclude(created_by=request.user).filter(is_general=False)
    courses = Course.objects.all()

    context = {
        'private_banks': private_banks,
        'staff_banks': staff_banks,
        'courses': courses,
    }
    return render(request, 'staff_create_quiz.html', context)


def get_departments(request, faculty_id):
    departments = Department.objects.filter(faculty_id=faculty_id).values('id', 'name')
    return JsonResponse({'departments': list(departments)})    

@login_required
def available_quizzes_view(request):
    quizzes = Quiz.objects.filter(
        visibility_to_students=True,
        is_open=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    )
    return render(request, 'student/available_quizzes.html', {'quizzes': quizzes})



@login_required
def start_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Check if already attempted
    if StudentQuizAttempt.objects.filter(student=request.user, quiz=quiz, is_submitted=True).exists():
        messages.warning(request, "You have already taken this quiz.")
        return redirect('available_quizzes')

    # Get or create attempt
    attempt, created = StudentQuizAttempt.objects.get_or_create(
        student=request.user, quiz=quiz, is_submitted=False
    )

    # If first time, assign random questions
    if created or not StudentQuizQuestion.objects.filter(attempt=attempt).exists():
        all_questions = list(Question.objects.filter(bank=quiz.source_bank))
        if len(all_questions) < quiz.number_of_questions:
            messages.error(request, "❌ Not enough questions in the question bank.")
            return redirect('available_quizzes')

        random_questions = random.sample(all_questions, quiz.number_of_questions)
        StudentQuizQuestion.objects.bulk_create([
            StudentQuizQuestion(attempt=attempt, question=q) for q in random_questions
        ])

    # Get the questions for this attempt
    assigned_questions = StudentQuizQuestion.objects.filter(attempt=attempt).select_related('question')

    return render(request, 'student/take_quiz.html', {
        'quiz': quiz,
        'attempt': attempt,
        'questions': [sq.question for sq in assigned_questions]
    })


@require_POST
@login_required
def submit_quiz_view(request, attempt_id):
    attempt = get_object_or_404(StudentQuizAttempt, id=attempt_id, student=request.user)

    if attempt.is_submitted:
        return HttpResponse("Already submitted.")



    assigned_questions = StudentQuizQuestion.objects.filter(attempt=attempt).select_related('question')

    score = 0
    total = assigned_questions.count()

    for sq in assigned_questions:
        question = sq.question
        selected = request.POST.get(f"question_{question.id}")
        if selected:
            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected
            )
            if selected == question.correct_option:
                score += 1

    percentage = (score / total) * 100 if total > 0 else 0

    attempt.score = percentage
    attempt.is_submitted = True
    attempt.submitted_at = timezone.now()
    attempt.save()

    messages.success(request, f"✅ Quiz submitted successfully! Score: {percentage:.2f}%")
    return redirect('quiz_result', attempt_id=attempt.id)
# views.py
def resume_quiz_view(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user, completed=False)
    return redirect('take_quiz', quiz_id=attempt.quiz.id)  # or your actual take-quiz view

@login_required
def quiz_instructions_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Check that quiz is open and within date range
    now = timezone.now()
    if not quiz.is_open or now < quiz.start_time or now > quiz.end_time:
        messages.error(request, "This quiz is not available at the moment.")
        return redirect('student_dashboard')

    # If student already completed all attempts, block them
    attempts = QuizAttempt.objects.filter(student=request.user, quiz=quiz).count()
    if attempts >= quiz.allowed_attempts:
        messages.warning(request, "You have already used all allowed attempts.")
        return redirect('student_dashboard')

    context = {
        'quiz': quiz,
        'attempts_used': attempts,
        'remaining_attempts': quiz.allowed_attempts - attempts
    }
    return render(request, 'take_quiz.html', context)



@require_POST
@login_required
def start_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Same availability checks
    now = timezone.now()
    if not quiz.is_open or now < quiz.start_time or now > quiz.end_time:
        messages.error(request, "Quiz is not available.")
        return redirect('student_dashboard')

    # Check attempts
    attempts = QuizAttempt.objects.filter(student=request.user, quiz=quiz).count()
    if attempts >= quiz.allowed_attempts:
        messages.error(request, "All attempts used.")
        return redirect('student_dashboard')

    # Create new attempt
    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz,
        started_at=now
    )
    
    return redirect('take_quiz', attempt_id=attempt.id)


