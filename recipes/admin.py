from django.contrib import admin
from .models import Recipe, Ingredient, RecipeIngredient, UserProfile, Inventory, Feedback, Tag, Unit, Category

# Register your models here.

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(UserProfile)
admin.site.register(Inventory)
admin.site.register(Feedback)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Unit)