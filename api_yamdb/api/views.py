from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filtersets import TitleFilter
from .mixins import CreateListViewSet
from .pagination import CustomPagination
from .permissions import (AdminOrReadOnly, IsAdmin,
                          IsAdminModeratorAuthorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleCreateSerializer, TitleListSerializer,
                          TokenSerializer, UserSerializer)


class CategoryViewSet(CreateListViewSet):
    """
    Вьюсет для обработки [GET, POST, DELETE] запросов
    к объектам модели Category.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListViewSet):
    """
    Вьюсет для обработки [GET, POST, DELETE] запросов
    к объектам модели Genre.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для обработки [GET, POST, PATCH, DELETE] запросов
    к объектам модели Title.
    """

    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering = ("name",)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleListSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для обработки [GET, POST, PATCH, DELETE] запросов
    к объектам модели Review.
    """

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAdminModeratorAuthorOrReadOnly,
        IsAuthenticatedOrReadOnly,
    )
    pagination_class = CustomPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title(),
        )


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для обработки [GET, POST, PATCH, DELETE] запросов
    к объектам модели Comment.
    """

    serializer_class = CommentSerializer
    permission_classes = (
        IsAdminModeratorAuthorOrReadOnly,
        IsAuthenticatedOrReadOnly,
    )
    pagination_class = CustomPagination

    def get_comment(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_comment().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_comment(),
        )


class GetJWTToken(viewsets.ModelViewSet):
    serializer_class = TokenSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        confirmation_code = serializer.validated_data["confirmation_code"]
        user = get_object_or_404(User, username=username)

        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response({"token": f"{token}"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpViewSet(viewsets.ModelViewSet):
    serializer_class = SignUpSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        confirmation_code = default_token_generator.make_token(user)
        mail_subject = "Код подтверждения"
        message = f"Ваш код подтверждения: {confirmation_code}"
        send_mail(
            mail_subject,
            message,
            f"Yamdb <{settings.EMAIL_ADMIN}>",
            [user.email],
        )

        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "username",
    ]
    lookup_field = "username"

    @action(
        detail=False,
        url_path="me",
        methods=["GET", "PATCH"],
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def get_self_user_page(self, request):
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
        else:
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(
                role=request.user.role,
                partial=True
            )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["DELETE"],
    )
    def delete_user(self, request):
        if not request.user.is_superuser:
            return Response(
                {"detail": "У вас нет прав на удаление пользователей"},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = get_object_or_404(User, username=request.data["username"])
        user.delete()
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response(
                {"detail": "Метод PUT не разрешен"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().update(request, *args, **kwargs)
