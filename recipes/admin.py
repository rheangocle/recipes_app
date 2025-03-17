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
    FodmapCategory,
    RecipeIngredient,
    Feedback,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ["ingredient", "unit"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["title", "cuisine", "total_time", "servings", "fodmap_friendly"]
    list_filter = ["cuisine", "fodmap_friendly", "tags"]
    search_fields = ["title", "description", "instructions"]
    inlines = [RecipeIngredientInline]
    filter_horizontal = ["tags"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("title", "description", "instructions", "image")}),
        (
            "Recipe Details",
            {
                "fields": (
                    "cuisine",
                    "prep_time",
                    "cook_time",
                    "total_time",
                    "servings",
                    "tags",
                )
            },
        ),
        ("FODMAP Information", {"fields": ("fodmap_friendly", "fodmap_notes")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse")}),
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "fodmap_category", "default_unit"]
    list_filter = ["category", "fodmap_category"]
    search_fields = ["name"]
    autocomplete_fields = ["category", "fodmap_category", "default_unit", "substitutes"]
    filter_horizontal = ["substitutes"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name", "description"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name", "description"]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["name", "unit_type"]
    list_filter = ["unit_type"]
    search_fields = ["name"]


@admin.register(FodmapCategory)
class FodmapCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name", "description"]


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ["user", "ingredient", "quantity", "unit", "expiry_date"]
    list_filter = ["user", "expiry_date"]
    search_fields = ["user__username", "ingredient__name"]
    autocomplete_fields = ["user", "ingredient", "unit"]

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user','recipe','rating','created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'recipe__title', 'comments']
    autocomplete_fields = ['user','recipe']
    readonly_fields = ['created_at']
    
@admin.register(DietType)
class DietTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    
@admin.register(DietaryRestriction)
class DietaryRestrictionAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']

@admin.register(FoodPreference)
class FoodPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'ingredient','preference']
    list_filter = ['preference']
    search_fields = ['user__username','ingredient__name']
    autocomplete_fields = ['user','ingredient']
    
@admin.register(RecipePreference)
class RecipePreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe','preference']
    list_filter = ['preference']
    search_fields = ['user__username','recipe__title']
    autocomplete_fields = ['user','recipe']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'diet_type', 'created_at', 'updated_at']
    list_filter = ['diet_type', 'dietary_restrictions']
    search_fields = ['user__username', 'user__email']
    autocomplete_fields = ['user', 'diet_type']
    filter_horizontal = ['dietary_restrictions', 'preferences']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'diet_type')
        }),
        ('Restrictions and Preferences', {
            'fields': ('dietary_restrictions', 'preferences')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'quantity', 'unit']
    list_filter = ['recipe', 'ingredient']
    search_fields = ['recipe__title', 'ingredient__name']
    autocomplete_fields = ['recipe', 'ingredient', 'unit']