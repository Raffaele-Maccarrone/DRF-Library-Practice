from django.utils import timezone
from borrowings.telegram import send_telegram_message
from borrowings.models import Borrowing


def notify_overdue_borrowings():
    today = timezone.localdate()

    overdue_borrowings = Borrowing.objects.select_related(
        "book", "user"
    ).filter(
        expected_return_date__lt=today,
        actual_return_date__isnull=True,
    )
    for borrowing in overdue_borrowings:
        message = (
            "⚠️ Overdue Borrowing!\n"
            f"Book: {borrowing.book.title}\n"
            f"User: {borrowing.user.email}\n"
            f"Expected return: {borrowing.expected_return_date}\n"
        )
        send_telegram_message(message)
