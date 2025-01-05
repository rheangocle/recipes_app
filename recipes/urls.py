from rest_framework.routers import DefaultRouter
from .views import (
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    FeedbackViewSet,
    InventoryViewSet,
    CategoryViewSet,
    UserProfileViewSet
)

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'users', UserProfileViewSet, basename='users')

urlpatterns = router.urls
