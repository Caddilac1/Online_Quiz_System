from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import StudentRegistrationForm, StaffRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
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
    if request.method == 'POST':
        full_name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        index_number = request.POST.get('index-number', '').strip()  # student_id

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

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'student_signup.html')

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
            student_id=index_number
        )

        # === Send Email Verification ===
        send_verification_email(user, request)
        return render(request, 'email_sent.html', {'user': user})


        messages.success(request, "Account created! Please check your email to verify your account.")
        return redirect('login')

    return render(request, 'student_signup.html')

def register_staff(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        staff_id = request.POST.get('staff_id', '').strip()
        faculty = request.POST.get('faculty')
        department = request.POST.get('department')
        position = request.POST.get('position')
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        errors = []

        if not full_name:
            errors.append("Full name is required.")
        if not staff_id:
            errors.append("Staff ID is required.")
        if not email or '@' not in email:
            errors.append("Valid email is required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if CustomUser.objects.filter(email=email).exists():
            errors.append("An account with this email already exists.")
        if StaffProfile.objects.filter(staff_id=staff_id).exists():
            errors.append("This staff ID is already registered.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'staff_signup.html')

        # Split name
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        # Create the user with is_active=False (pending activation)
        user = CustomUser.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type='staff',
            is_active=False,
            password=make_password(password)
        )

        # Create staff profile
        StaffProfile.objects.create(
            user=user,
            staff_id=staff_id,
            faculty=faculty,
            department=department,
            position=position
        )

        send_staff_activation_email(user, request)
        return render(request, 'email_sent.html', {'user': user})

        # Notify admin to activate
        notify_admin_of_staff_registration(user, staff_id)

        return render(request, 'staff_registration_success.html', {'email': email})

    return render(request, 'staff_signup.html')

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
    message = render_to_string('notify_admin.html', {
        'staff': user,
        'staff_id': staff_id,
    })

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],  # e.g., admin@gctu.edu.gh
        fail_silently=False,
    )


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'email_verified.html')
    else:
        return render(request, 'email_failed.html')



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
    if hasattr(request.user, 'studentprofile'):
        return render(request, 'student_dashboard.html', {'student': request.user.studentprofile})
    return redirect('login')

@login_required
def staff_dashboard(request):
    if hasattr(request.user, 'staffprofile'):
        return render(request, 'staff_dashboard.html', {'staff': request.user.staffprofile})
    return redirect('login')