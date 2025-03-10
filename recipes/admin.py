from django.contrib import admin
from .models import (
    Recipe,
    Ingredient,
    UserProfile,
    Inventory,
    Feedback,
    Tag,
    Unit,
    Category,
    DietaryRestriction,
    DietType,
    FoodPreference,
    RecipePreference,
    FodmapCategory
)

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(UserProfile)
admin.site.register(Inventory)
admin.site.register(Feedback)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Unit)
admin.site.register(DietaryRestriction)
admin.site.register(DietType)
admin.site.register(FoodPreference)
admin.site.register(RecipePreference)
admin.site.register(FodmapCategory)