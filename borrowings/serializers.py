from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from borrowings.telegram import send_telegram_message

class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
        read_only_fields = fields

class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "book",
            "expected_return_date",
        )

    def validate_book(self, value):
        if value.inventory <= 0:
            raise serializers.ValidationError(
                "Book is out of stock."
            )

        return value

    def create(self, validated_data):
        user = self.context["request"].user
        borrow_date = timezone.localdate()

        expected_return_date = validated_data["expected_return_date"]

        if expected_return_date < borrow_date:
            raise serializers.ValidationError({
                "expected_return_date": (
                    "Expected return date cannot be "
                    "earlier than borrow date."
                )
            })

        with transaction.atomic():
            book = Book.objects.select_for_update().get(
                pk=validated_data["book"].pk
            )

            if book.inventory <= 0:
                raise serializers.ValidationError({
                    "book": "Book is out of stock."
                })

            borrowing = Borrowing.objects.create(
                book=book,
                user=user,
                borrow_date=borrow_date,
                expected_return_date=expected_return_date,
            )

            book.inventory -= 1
            book.save(update_fields=["inventory"])
            message = (
                f"📚 New Borrowing!\n"
                f"Book: {book.title}\n"
                f"By user: {user.email}\n"
                f"Borrowing date: {borrow_date}\n"
                f"Expected return: {expected_return_date}\n"
            )
            transaction.on_commit(
                lambda: send_telegram_message(message),
                robust=True,
            )

        return borrowing
