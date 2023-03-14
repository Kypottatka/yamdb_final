from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
    UserViewSet,
    SignUpViewSet,
    GetJWTToken,
)


v1_router = DefaultRouter()
v1_router.register("titles", TitleViewSet, basename="title")
v1_router.register(
    r"titles/(?P<title_id>[\d]+)/reviews", ReviewViewSet, basename="review"
)
v1_router.register(
    r"titles/(?P<title_id>[\d]+)/reviews/(?P<review_id>[\d]+)/comments",
    CommentViewSet,
    basename="comment",
)
v1_router.register("categories", CategoryViewSet, basename="category")
v1_router.register("genres", GenreViewSet, basename="genre")

users_router = DefaultRouter()
users_router.register(
    "users",
    UserViewSet,
    basename="users",
)
users_router.register(
    "signup",
    SignUpViewSet,
    basename="signup",
)
users_router.register(
    "token",
    GetJWTToken,
    basename="token",
)


urlpatterns = [
    path("v1/", include(v1_router.urls)),
    path("v1/", include(users_router.urls)),
    path("v1/auth/", include(users_router.urls)),
    path("v1/auth/", include("django.contrib.auth.urls")),
]
