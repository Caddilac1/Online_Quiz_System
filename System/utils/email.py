from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = request.build_absolute_uri(f"/activate/{uid}/{token}/")

    subject = 'Activate Your Account - GCTU Online Exams System'
    message = render_to_string('email_template.html', {
        'user': user,
        'activation_link': activation_link,
    })

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_staff_approval_email(staff_user):
    subject = "Your GCTU Staff Account Has Been Approved"
    
    html_content = render_to_string("staff_approved.html", {
        'full_name': staff_user.get_full_name(),
        'site_name': "GCTU Exams System",
        'login_url': "http://127.0.0.1:8000/login/",  # Update if deployed
    })

    email = EmailMultiAlternatives(
        subject=subject,
        body="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[staff_user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()