from django.db import models
from django.conf import settings
from books.models import Book

from django.core.exceptions import ValidationError


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(
        null=True,
        blank=True
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def clean(self):
        super().clean()

        if self.expected_return_date < self.borrow_date:
            raise ValidationError({
                "expected_return_date": (
                    "Expected return date cannot be "
                    "earlier than borrow date."
                )
            })

        if (self.actual_return_date is not None
                and self.actual_return_date < self.borrow_date):
            raise ValidationError({
                "actual_return_date": (
                    "Actual return date cannot be"
                    " earlier than borrow date."
                )
            })
