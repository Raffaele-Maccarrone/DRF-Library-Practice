from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import (
    UserRegistrationView,
    UserProfileView,
)


urlpatterns = [
    path(
        "",
        UserRegistrationView.as_view(),
        name="user-register",
    ),
    path(
        "me/",
        UserProfileView.as_view(),
        name="user-profile",
    ),
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]
