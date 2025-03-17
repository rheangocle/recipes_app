from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.viewsets import (
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    FeedbackViewSet,
    InventoryViewSet,
    CategoryViewSet,
    UserProfileViewSet,
    DietTypeViewSet,
    DietaryRestrictionViewSet,
    FoodPreferenceViewSet,
    RecipePreferenceViewSet,
    FodmapCategoryViewSet,
    UnitViewSet,
    RecipeIngredientViewSet,
)

from .views.update_recipe_view import UpdateFODMAPRecipeView
from .views.generate_recipe_view import FODMAPRecipeGeneratorView

router = DefaultRouter()
router.register(r"ingredients", IngredientViewSet, basename="ingredient")
router.register(r"recipes", RecipeViewSet, basename="recipe")
router.register(r"recipe-ingredients", RecipeIngredientViewSet)
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"feedback", FeedbackViewSet, basename="feedback")
router.register(r"inventory", InventoryViewSet, basename="inventory")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"user-profile", UserProfileViewSet, basename="user-profile")
router.register(r"diet-types", DietTypeViewSet, basename="diettype")
router.register(
    r"dietary-restrictions", DietaryRestrictionViewSet, basename="dietaryrestriction"
)
router.register(r"food-preferences", FoodPreferenceViewSet, basename="food-preferences")
router.register(
    r"recipe_preferences", RecipePreferenceViewSet, basename="recipe-preferences"
)
router.register(r"fodmap-categories", FodmapCategoryViewSet)
router.register(r"units", UnitViewSet)

urlpatterns = [
    path(
        "recipes/generate", FODMAPRecipeGeneratorView.as_view(), name="generate-recipe"
    ),
    path("recipes/update", UpdateFODMAPRecipeView.as_view(), name="update-recipe"),
    path("", include(router.urls)),
]
