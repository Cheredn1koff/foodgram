from django.contrib import admin

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Purchase,
    Recipe, Tag, Unit
)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    raw_id_fields = ('ingredient',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInline, )
    list_filter = ('author', 'tags')
    search_fields = ('name',)
    list_display = ('name', 'author', 'count_favorites')
    fields = (
        'name', 'author', 'tags', 'text', 'cooking_time', 'image',
        'count_favorites'
    )
    readonly_fields = ('count_favorites',)

    def count_favorites(self, instance):
        count = Favorite.objects.filter(
            recipe=instance
        ).count()
        measurment_unit = 'раз'
        measurment_unit += 'а' if str(count)[-1] in '234' else ''
        return f'{count} {measurment_unit}'

    count_favorites.short_description = 'Добавлено в избранное'


class IngredientRecipeAdmin(admin.ModelAdmin):
    search_fields = ('inrgedient',)


class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', 'measurement_unit')

    def measurement_unit(self, obj):
        return obj.measurement_unit.name


admin.site.register(Unit)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Purchase)
admin.site.register(Favorite)
