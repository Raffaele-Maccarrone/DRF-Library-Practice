from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)

@extend_schema_view(
    get=extend_schema(
        summary="List borrowings",
        description="Retrieve a list of library borrowings.",
        tags=["Borrowings"],
    )
)
class BorrowingListView(generics.ListAPIView):
    queryset = Borrowing.objects.select_related(
        "book", "user"
    ).all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAdminUser]

@extend_schema_view(
    get=extend_schema(
        summary="Retrieve borrowing",
        description="Retrieve details of a specific borrowing.",
        tags=["Borrowings"],
    )
)
class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.select_related(
        "book", "user"
    ).all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAdminUser]
