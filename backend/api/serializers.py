from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer
)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from api.utils import collect_ingredientsrecipe_objects, collect_tags
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Purchase,
    Recipe, Tag
)
from users.models import Subscription


User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
            'id'
        )
        read_only_fields = ('id', )


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'id',
            'is_subscribed'
        )
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('id', 'name', 'color', 'slug')

    def to_internal_value(self, data):
        return data


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit.name'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')
        read_only_fields = ('name', 'measurement_unit')


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(default=serializers.CurrentUserDefault())
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(many=True, required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ('pub_date', )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['author', 'name', 'text', 'cooking_time']
            )
        ]

    def is_authenticated(func):
        def wrapper(self, obj):
            if self.context.get('request').user.is_anonymous:
                return False
            return func(self, obj)
        return wrapper

    @is_authenticated
    def get_is_in_shopping_cart(self, obj):
        return Purchase.objects.filter(
            user=self.context.get('request').user,
            recipe=obj
        ).exists()

    @is_authenticated
    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.context.get('request').user,
            recipe=obj
        ).exists()

    def validate_ingredients(self, data):
        if len(data) == 0:
            raise ValidationError(
                'Список ингредиентов не может быть пустым'
            )
        seen_ingredinets = set()
        for ingredient in data:
            ingredient_id = ingredient['ingredient']['id']
            if ingredient_id in seen_ingredinets:
                raise ValidationError(
                    'Ингредиенты должны быть уникальными'
                )
            seen_ingredinets.add(ingredient_id)

            if ingredient.get('amount') < 1:
                raise ValidationError(
                    'Убедитесь, что значение указателя ингредиента больше 0'
                )
        if (
            Ingredient.objects.filter(id__in=seen_ingredinets).count()
            != len(seen_ingredinets)
        ):
            raise ValidationError('Указанного ингредиента не существует')
        return data

    def validate_tags(self, data):
        if len(data) == 0:
            raise ValidationError(
                'Список тегов не может быть пустым'
            )
        for tag_id in data:
            if not isinstance(tag_id, int) or tag_id < 1:
                raise ValidationError(
                    'Убедитесь, что значение указателя тега больше 0'
                )
        if (
            Tag.objects.filter(id__in=data).count()
            != len(data)
        ):
            raise ValidationError('Указанного тега не существует')
        return super().validate(data)

    def validate_cooking_time(self, data):
        if data < 1:
            raise ValidationError(
                'Убедитесь, что значение времени приготовления больше 0'
            )
        return data

    def create(self, validated_data):
        tag_data = validated_data.pop('tags')
        ingredient_data = validated_data.pop('ingredients')
        recipe = Recipe(**validated_data)
        ingredientrecipe_objects = collect_ingredientsrecipe_objects(
            ingredient_data, recipe
        )
        tags = collect_tags(tag_data)
        recipe.save()
        IngredientRecipe.objects.bulk_create(
            ingredientrecipe_objects
        )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            IngredientRecipe.objects.filter(recipe=instance).delete()
            IngredientRecipe.objects.bulk_create(
                collect_ingredientsrecipe_objects(
                    ingredients,
                    instance
                )
            )
        if 'tags' in validated_data:
            tags = collect_tags(validated_data.pop('tags'))
            instance.tags.set(tags)
        super().update(instance, validated_data)
        return instance


class FavoritePurchaseSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('user')
        representation.pop('recipe')
        return representation


class FavoriteSerializer(FavoritePurchaseSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe']
            )
        ]


class PurchaseSerializer(FavoritePurchaseSerializer):

    class Meta:
        model = Purchase
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Purchase.objects.all(),
                fields=['user', 'recipe']
            )
        ]


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscriptionSerializer(
    serializers.ModelSerializer
):
    recipes_count = serializers.ReadOnlyField(
        source='author.recipes.count'
    )
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    email = serializers.ReadOnlyField(source='author.email')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_recipes(self, obj):
        serializer = RecipeShortSerializer(obj.author.recipes, many=True)
        request = self.context.get('request')
        recipes_limit = (
            request.parser_context['request'].
            query_params.get('recipes_limit')
        )
        recipes = obj.author.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                raise ValidationError({
                    'errors': (
                        'recipes_limit - целое положительное число'
                    )
                })
            except AssertionError:
                raise ValidationError({
                    'errors': (
                        'recipes_limit - целое положительное число'
                    )
                })
        serializer = RecipeShortSerializer(recipes, many=True)
        return serializer.data

    def get_is_subscribed(self, obj):
        return True
