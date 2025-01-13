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
)
from .views.generate_recipe_view import GenerateRecipeView


router = DefaultRouter()
router.register(r"ingredients", IngredientViewSet, basename="ingredient")
router.register(r"recipes", RecipeViewSet, basename="recipe")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"feedback", FeedbackViewSet, basename="feedback")
router.register(r"inventory", InventoryViewSet, basename="inventory")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"user-profile", UserProfileViewSet, basename="user-profile")

urlpatterns = [
    path("", include(router.urls)),
    path("generate-recipe/", GenerateRecipeView.as_view(), name="generate-recipe"),
]


# urlpatterns += [
#     path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
# ]
