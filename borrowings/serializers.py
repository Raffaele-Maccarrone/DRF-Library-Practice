from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing

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
