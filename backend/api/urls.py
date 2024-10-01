from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    FavoriteViewSet, IngredientViewSet, PurchaseViewSet,
    RecipeViewSet, TagViewSet, UserViewSet
)

user_router = DefaultRouter()
user_router.register(
    'users',
    UserViewSet,
    basename='users'
)

router = DefaultRouter()
router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorites'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    PurchaseViewSet,
    basename='purchases'
)

router.urls.extend([
    url for url in user_router.urls if url.name
    in settings.ALLOWED_USER_ACTIONS
])

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
