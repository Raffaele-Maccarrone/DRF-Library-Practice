from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from books.models import Book
from books.serializers import BookSerializer
from books.permissions import IsAdminOrReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="List books",
        description="Retrieve a list of all books.",
        tags=["Books"],
    ),
    retrieve=extend_schema(
        summary="Retrieve book",
        description="Retrieve details of a specific book.",
        tags=["Books"],
    ),
    create=extend_schema(
        summary="Create book",
        description="Create a new book in the library.",
        tags=["Books"],
    ),
    update=extend_schema(
        summary="Update book",
        description="Update all fields of a book.",
        tags=["Books"],
    ),
    partial_update=extend_schema(
        summary="Partially update book",
        description="Update selected fields of a book.",
        tags=["Books"],
    ),
    destroy=extend_schema(
        summary="Delete book",
        description="Remove a book from the library.",
        tags=["Books"],
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
