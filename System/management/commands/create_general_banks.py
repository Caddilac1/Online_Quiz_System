from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from System.models import Course, QuestionBank
User = get_user_model()

class Command(BaseCommand):
    help = "Create general question banks for all courses"

    def handle(self, *args, **kwargs):
        # Use the first superuser or any default admin
        default_admin = User.objects.filter(is_superuser=True).first()
        if not default_admin:
            self.stdout.write(self.style.ERROR("❌ No superuser found. Cannot set `created_by`."))
            return

        count = 0
        for course in Course.objects.all():
            bank, created = QuestionBank.objects.get_or_create(
                course=course,
                is_general=True,
                defaults={
                    'title': course.title,
                    'created_by': default_admin
                }
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created bank for {course.title}"))
            else:
                self.stdout.write(f"⚠️ Bank already exists for {course.title}")

        self.stdout.write(self.style.SUCCESS(f"🎉 Done. {count} new banks created."))
