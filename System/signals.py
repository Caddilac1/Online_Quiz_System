from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import QuestionBank, GoogleSheetQuiz

@receiver(post_save, sender=QuestionBank)
def auto_create_google_sheet_quiz(sender, instance, created, **kwargs):
    if created and instance.is_general:
        GoogleSheetQuiz.objects.get_or_create(question_bank=instance)
