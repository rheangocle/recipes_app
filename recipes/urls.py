from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = router.urls
