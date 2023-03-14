from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import IntegrityError
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User
from users.validators import username_validator


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор модели Category."""

    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор модели Genre."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор модели Title для [POST, PATCH]-запросов."""

    genre = serializers.SlugRelatedField(
        many=True,
        write_only=True,
        slug_field="slug",
        required=False,
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        many=False,
        write_only=True,
        slug_field="slug",
        required=False,
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
        )


class TitleListSerializer(serializers.ModelSerializer):
    """Сериализатор модели Title для [GET]-запросов."""

    category = CategorySerializer(many=False, required=False)
    genre = GenreSerializer(many=True, required=False)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )
        read_only_fields = ("genre", "category", "rating")


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели Review."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")

    def validate(self, data):
        is_exist = Review.objects.filter(
            author=self.context["request"].user,
            title=self.context["view"].kwargs.get("title_id"),
        ).exists()
        if is_exist and self.context["request"].method == "POST":
            raise serializers.ValidationError(
                "Вы уже оставляли отзыв на это произведение."
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comment."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    review = serializers.SlugRelatedField(
        slug_field="text",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "bio",
            "role",
        )
        lookup_field = "username"
        extra_kwargs = {
            "email": {"required": True},
            "url": {"lookup_field": "username"},
        }


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.USER_FIELD_LENGTH,
        required=True,
        validators=[
            username_validator,
            UnicodeUsernameValidator(),
        ],
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH,
        required=True,
    )

    def create(self, validated_data):
        try:
            return User.objects.get_or_create(**validated_data)[0]
        except IntegrityError:
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
