from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
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
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'user-profile', UserProfileViewSet, basename='user-profile')

urlpatterns = router.urls

# urlpatterns += [
#     path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
# ]
