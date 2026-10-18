from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer


class BorrowingListView(generics.ListAPIView):
    queryset = Borrowing.objects.select_related(
        "book", "user"
    ).all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAdminUser]


class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.select_related(
        "book", "user"
    ).all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAdminUser]
