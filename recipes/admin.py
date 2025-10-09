from django.contrib import admin
from .models import (
    Recipe,
    Ingredient,
    IngredientAlias,
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
from .models.policy import DietTypeRule, RestrictionRule, DietProtocol, DietProtocolRule, UserProtocol


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
    
class IngredientAliasInline(admin.TabularInline):
    model = IngredientAlias
    extra = 1

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_filter = ("tags",)
    filter_horizontal = ("tags",)
    inlines = [IngredientAliasInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "description")


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
    
class DietTypeRuleInline(admin.TabularInline):
    model = DietTypeRule
    extra = 1
    
@admin.register(DietType)
class DietTypeAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    inlines = [DietTypeRuleInline]

class RestrictionRuleInline(admin.TabularInline):
    model = RestrictionRule
    extra = 1
    
@admin.register(DietaryRestriction)
class DietaryRestrictionAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    inlines = [RestrictionRuleInline]
    
class DietProtocolRuleInline(admin.TabularInline):
    model = DietProtocolRule
    extra = 1
    
@admin.register(DietProtocol)
class DietProtocolAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    inlines = [DietProtocolRuleInline]
    
@admin.register(UserProtocol)
class UserProtocolAdmin(admin.ModelAdmin):
    list_display = ("user", "protocol", "phase", "is_primary")
    list_filter = ("is_primary", "phase", "protocol")
    search_fields = ("user__username", "protocol__name")

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
    list_display = ['user', 'diet_types_display', 'created_at', 'updated_at']
    list_filter = ['diet_types', 'dietary_restrictions']
    search_fields = ['user__username', 'user__email']
    autocomplete_fields = ['user']
    filter_horizontal = ['diet_types', 'dietary_restrictions', 'preferences']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'diet_types')
        }),
        ('Restrictions and Preferences', {
            'fields': ('dietary_restrictions', 'preferences')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def diet_types_display(self, obj):
        return ", ".join([dt.name for dt in obj.diet_types.all()])
    diet_types_display.short_description = 'Diet Types'

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'quantity', 'unit']
    list_filter = ['recipe', 'ingredient']
    search_fields = ['recipe__title', 'ingredient__name']
    autocomplete_fields = ['recipe', 'ingredient', 'unit']
