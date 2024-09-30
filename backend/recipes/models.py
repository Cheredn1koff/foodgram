from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from core.validators import hex_color_validator


User = get_user_model()


class StringRepresentationMixin:

    def __str__(self):
        return self.name[:settings.STR_SYMBOLS_AMOUNT]


class Unit(StringRepresentationMixin, models.Model):
    name = models.CharField(
        verbose_name='единица измерения',
        max_length=settings.MAX_LENGTH_UNIT_NAME
    )

    class Meta:
        verbose_name = 'Единицы измерения'
        verbose_name_plural = 'Единицы измерений'


class Ingredient(StringRepresentationMixin, models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=settings.MAX_LENGTH_INGREDIENT_NAME,
    )
    measurement_unit = models.ForeignKey(
        Unit,
        verbose_name='единица измерения',
        related_name='ingredients',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return super().__str__() + f', {self.measurement_unit.name}'


class Tag(StringRepresentationMixin, models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=settings.MAX_LENGTH_TAG_NAME,
        unique=True
    )
    color = models.CharField(
        verbose_name='HEX цвет',
        max_length=settings.MAX_LENGTH_TAG_COLOR,
        validators=(hex_color_validator,),
        unique=True
    )
    slug = models.SlugField(verbose_name='slug', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return (
            f'{self._meta.verbose_name} '
            f'пользователя {self.user.get_username()}, '
            f'рецепт {self.recipe.name}'
        )


class Purchase(UserRecipe):

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_purchase'
            ),
        ]


class Favorite(UserRecipe):

    class Meta:
        ordering = ('id',)
        verbose_name_plural = verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        ]


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        'Ingredient',
        verbose_name='ингредиент',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='ingredients'
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(
            limit_value=settings.INGREDIENT_MIN_AMOUNT,
            message='Количество ингредиентов - целое положительное число'
        )]
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'

    def __str__(self) -> str:
        return f'{self.ingredient.name} x {self.amount} для {self.recipe.name}'


class Recipe(StringRepresentationMixin, models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='автор публикации',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(verbose_name='название', max_length=200)
    image = models.ImageField(
        verbose_name='картинка',
        upload_to='recipe/images/',
    )
    text = models.TextField(verbose_name='описание',)
    tags = models.ManyToManyField(Tag, verbose_name='теги',)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления (мин)',
        validators=[MinValueValidator(
            limit_value=settings.RECIPE_MIN_COOKING_TIME,
            message='Время приготовления - целое положительное число'
        )]
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return super().__str__() + f' автор {self.author.get_username()}'

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name', 'text', 'cooking_time'],
                name='unique_recipe'
            ),
        ]
