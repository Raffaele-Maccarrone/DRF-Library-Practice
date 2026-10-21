from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_q.models import Schedule


class Command(BaseCommand):
    help = "Configure daily overdue borrowing notifications."

    def handle(self, *args, **options):
        tomorrow = timezone.localdate() + timedelta(days=1)

        next_run = timezone.make_aware(
            datetime.combine(tomorrow, time(9, 0)),
            timezone.get_current_timezone(),
        )

        schedule, created = Schedule.objects.update_or_create(
            name="Daily Overdue Notifications",
            defaults={
                "func": "borrowings.tasks.notify_overdue_borrowings",
                "schedule_type": Schedule.DAILY,
                "repeats": -1,
                "next_run": next_run,
            },
        )

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(f"{action} schedule: {schedule.name}")
        )
