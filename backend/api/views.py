from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import LimitPagination
from api.permissions import (
    IsAuthorAdminOrReadOnlyPermission,
    IsNotBannedPermission
)
from api.serializers import (
    FavoriteSerializer, IngredientSerializer,
    PurchaseSerializer, RecipeSerializer,
    SubscriptionSerializer, TagSerializer
)
from core.utils import render_to_pdf
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Purchase,
    Recipe, Tag
)
from users.models import Subscription, User


class UserViewSet(DjoserUserViewSet):
    pagination_class = LimitPagination
    http_method_names = ['get', 'post', 'delete']

    def destroy(self, *args, **kwargs):
        return Response(
            {'detail': 'Метод DELETE не разрешен.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(
        detail=False,
        methods=['get'],
        pagination_class=LimitPagination,
        permission_classes=(IsNotBannedPermission,)
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            subscriptions,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsNotBannedPermission,)
    )
    def subscribe(self, request, id):
        following_user = get_object_or_404(User, id=id)

        if request.method == 'POST':
            try:
                subscription = Subscription.objects.create(
                    user=request.user, author=following_user
                )
                serializer = SubscriptionSerializer(
                    subscription,
                    context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            except IntegrityError as e:
                return Response(
                    {'errors': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        subscription = get_object_or_404(
            Subscription, user=request.user, author=following_user
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = LimitPagination
    permission_classes = (IsAuthorAdminOrReadOnlyPermission,)

    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial'):
            return Response(
                {'detail': 'Метод PUT не разрешен.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsNotBannedPermission,)
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientRecipe.objects.filter(
                recipe__purchase__user=request.user
            ).values(
                'ingredient__name', 'ingredient__measurement_unit__name'
            ).annotate(total=Sum('amount'))
        )

        if not ingredients:
            return Response(
                {'details': 'В списке покупок нет ни одного рецепта'},
                status=status.HTTP_400_BAD_REQUEST
            )

        context = {
            'user': request.user,
            'ingredients': ingredients
        }
        pdf = render_to_pdf('api/pdf_template.html', context)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'inline; filename="{request.user.username}ShopingCart.pdf"'
        )
        return response


class FavoritePurchaseViewSet(
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthorAdminOrReadOnlyPermission, )
    http_method_names = ['post', 'delete']

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        request.data['recipe'] = kwargs.get('recipe_id')
        return super().create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class FavoriteViewSet(mixins.ListModelMixin, FavoritePurchaseViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_object(self):
        return get_object_or_404(
            Favorite,
            recipe=self.kwargs.get('recipe_id'),
            user=self.request.user.id
        )


class PurchaseViewSet(FavoritePurchaseViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

    def get_object(self):
        return get_object_or_404(
            Purchase,
            recipe=self.kwargs.get('recipe_id'),
            user=self.request.user.id
        )
