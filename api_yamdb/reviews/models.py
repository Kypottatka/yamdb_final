from api.validators import year_validator
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
        verbose_name="Название",
        help_text="Заполните имя категории",
    )
    slug = models.SlugField(
        unique=True,
        help_text="Поле с уникальным значением"
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
        verbose_name="Название",
        help_text="Заполните имя жанра",
    )
    slug = models.SlugField(
        unique=True,
        help_text="Поле с уникальным значением"
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
        verbose_name="Название",
        help_text="Заполните название произведения",
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="Год выпуска",
        help_text="Заполните год выпуска",
        validators=[year_validator],
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="описание",
        help_text="Заполните описание",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="titles",
        verbose_name="категория",
        help_text="Выберите категорию",
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name="genre",
        verbose_name="жанр",
        help_text="Выберите один или несколько жанров",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
    )
    text = models.CharField(
        max_length=1000,
        verbose_name="Текст отзыва",
        help_text="Введите текст отзыва",
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Оценка",
        validators=(
            MinValueValidator(1, message="Убедитесь, что оценка не меньше 1."),
            MaxValueValidator(
                10, message="Убедитесь, что оценка не больше 10."
            ),
        ),
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "title",
                    "author",
                ),
                name="unique-review",
            )
        ]
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    text = models.CharField(
        max_length=200,
        verbose_name="Текст комментария",
        help_text="Введите текст комментария",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text
