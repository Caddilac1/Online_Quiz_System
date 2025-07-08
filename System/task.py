from celery import shared_task
from django.utils import timezone
from .models import QuizAttempt

@shared_task
def auto_submit_quiz(attempt_id):
    try:
        attempt = QuizAttempt.objects.get(id=attempt_id)
        if not attempt.is_completed:
            # Example auto submission logic
            attempt.is_completed = True
            attempt.submitted_at = timezone.now()
            attempt.save()
            print(f"Auto-submitted attempt {attempt_id}")
    except QuizAttempt.DoesNotExist:
        print(f"QuizAttempt {attempt_id} not found.")
