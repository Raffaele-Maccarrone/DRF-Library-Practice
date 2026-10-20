from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db import transaction
from django.utils import timezone
from books.models import Book

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer, BorrowingCreateSerializer
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse
)

@extend_schema_view(
    get=extend_schema(
        summary="List borrowings",
        description="Retrieve a list of library borrowings.",
        tags=["Borrowings"],
    ),
    post=extend_schema(
        summary="Create borrowing",
        description=(
            "Create a borrowing for the authenticated user "
            "and decrease book inventory."
        ),
        tags=["Borrowings"],
    ),
)

class BorrowingListView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.select_related(
        "book", "user"
    ).all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [IsAdminUser()]

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

class BorrowingReturnView(generics.GenericAPIView):
    queryset = Borrowing.objects.select_related(
        "book", "user"
    ).all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Borrowing.objects.select_for_update()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    @extend_schema(
        summary="Return borrowing",
        description=(
                "Return a borrowed book and increase its inventory by one. "
                "Users can return their own borrowings, while staff "
                "members can return any borrowing."
        ),
        request=None,
        responses={
            200: OpenApiResponse(description="Borrowing returned successfully."),
            400: OpenApiResponse(description="Borrowing already returned."),
            401: OpenApiResponse(description="Authentication required."),
            404: OpenApiResponse(description="Borrowing not found or not accessible."),
        },
        tags=["Borrowings"],
    )

    def post(self, request, pk):
        with transaction.atomic():
            borrowing = self.get_object()
            if borrowing.actual_return_date is not None:
                return Response(
                    {"detail": "This borrowing has already been returned."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            book = Book.objects.select_for_update().get(
                pk=borrowing.book_id
            )
            borrowing.actual_return_date = timezone.localdate()
            borrowing.save(update_fields=["actual_return_date"])
            book.inventory += 1
            book.save(update_fields=["inventory"])
            return Response(
                {"detail": "Borrowing returned successfully."},
                status=status.HTTP_200_OK,
            )
