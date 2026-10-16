from django.contrib.auth import get_user_model
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
)
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
)

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        summary="Register a new user",
        description=(
            "Create a new user account using email, "
            "first name, last name, and password."
        ),
        request=UserRegistrationSerializer,
        responses={
            201: UserRegistrationSerializer,
            400: OpenApiResponse(
                description="Invalid registration data."
            ),
        },
        tags=["Users"],
        auth=[],
    )
)
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve current user profile",
        description=(
            "Return the profile information "
            "of the authenticated user."
        ),
        responses={
            200: UserProfileSerializer,
            401: OpenApiResponse(
                description="Authentication required."
            ),
        },
        tags=["Users"],
    ),
    put=extend_schema(
        summary="Update current user profile",
        description=(
            "Update the authenticated user's profile."
        ),
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            401: OpenApiResponse(
                description="Authentication required."
            ),
        },
        tags=["Users"],
    ),
    patch=extend_schema(
        summary="Partially update current user profile",
        description=(
            "Update selected fields of the "
            "authenticated user's profile."
        ),
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            401: OpenApiResponse(
                description="Authentication required."
            ),
        },
        tags=["Users"],
    ),
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
