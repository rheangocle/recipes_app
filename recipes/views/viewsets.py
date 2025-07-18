# pylint: disable=no-member

from logging import config
from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    Inventory,
    Feedback,
    Category,
    UserProfile,
    DietaryRestriction,
    DietType,
    FoodPreference,
    RecipePreference,
    FodmapCategory,
    Unit,
    RecipeIngredient,
)
from recipes.serializers import (
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    InventorySerializer,
    FeedbackSerializer,
    CategorySerializer,
    UserProfileSerializer,
    DietaryRestrictionSerializer,
    DietTypeSerializer,
    FoodPreferenceSerializer,
    RecipePreferenceSerializer,
    FodmapCategorySerializer,
    UnitSerializer,
    RecipeIngredientSerializer,
)
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class BaseViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]


class IngredientViewSet(BaseViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    filterset_fields = ["category__id", "fodmap_category__id"]

    search_fields = ["name"]

    ordering_fields = ["name", "category__name"]
    ordering = ["name"]

    @action(detail=False, methods=["post"])
    def auto_complete(self, request):
        search_term = request.data.get("search_term", "")
        results = self.queryset.filter(name__icontains=search_term)[:10]
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


class RecipeViewSet(BaseViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    filterset_fields = ["tags", "cuisine", "fodmap_friendly"]

    search_fields = ["title", "description"]

    ordering_fields = ["created_at", "title", "total_time"]
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"])
    def fodmap_friendly(self, request):
        """Get only FODMAP friendly recipes"""
        recipes = self.queryset.filter(fodmap_friendly=True)
        page = self.paginate_queryset(recipes)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def by_ingredients(self, request):
        """Find recipes by given ingredients"""
        ingredient_ids = request.query_params.getList('ingredients')
        if not ingredient_ids:
            return Response({'error': "No ingredients provided"}, status=400)
        
        recipes = Recipe.objects.filter(ingredients__id__in=ingredient_ids).distinct())
        page = self.paginate_queryset(recipes)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def favorites(self, request):
        """Get user's favorite recipes"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, 401)
        
        favorite_recipes = Recipe.objects.filter(
            user_preferences__user=request.user,
            user_preferences__preference='favorite'
            )
        page = self.paginate_queryset(favorite_recipes)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(favorite_recipes, many=True)
        return Response(serializer.data)


class RecipeIngredientViewSet(BaseViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer

    filterset_fields = ["recipe__id", "ingredient__id"]
    search_fields = ["ingredient__name", "recipe__title"]
    ordering_fields = ["recipe__title", "ingredient__name"]
    ordering = ["recipe__title"]


class TagViewSet(BaseViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    filterset_fields = ["name"]

    search_fields = ["name"]

    ordering_fields = ["name"]
    ordering = ["name"]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [permissions.IsAdminUser]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    filterset_fields = ["name"]

    search_fields = ["name"]

    ordering_fields = ["name"]


class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()

    filterset_fields = ["unit_type"]

    search_fields = ["name"]

    ordering_fields = ["name"]
    ordering = ["name"]


class FodmapCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FodmapCategorySerializer
    queryset = FodmapCategory.objects.all()

    filterset_fields = ["name"]

    search_fields = ["name"]

    ordering_fields = ["name"]
    ordering = ["name"]


class InventoryViewSet(BaseViewSet):
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["ingredient__name", "quantity", "expiry_date"]

    search_fields = ["ingredient__name"]

    ordering_fields = ["quantity", "ingredient__name", "expiry_date"]
    ordering = ["ingredient__name"]

    def get_queryset(self):
        return Inventory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FeedbackViewSet(BaseViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["recipe", "created_at", "rating"]

    search_fields = ["recipe__title", "recipe__cuisine", "comments", "rating"]

    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserProfileViewSet(BaseViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["diet_type"]

    search_fields = ["dietary_restrictions__name"]

    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            profile = UserProfile.objects.get(user=self.request.user)
            serializer.instance = profile
            serializer.save()
        except UserProfile.DoesNotExist:
            serializer.save(user=self.request.user)


class DietTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DietType.objects.all()
    serializer_class = DietTypeSerializer
    permission_classes = [permissions.AllowAny]


class DietaryRestrictionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DietaryRestriction.objects.all()
    serializer_class = DietaryRestrictionSerializer
    permission_classes = [permissions.AllowAny]


class FoodPreferenceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FoodPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["ingredient", "preference"]
    search_fields = ["ingredient__name"]
    ordering_fields = ["preference", "ingredient__name"]
    ordering = ["preference"]

    def get_queryset(self):
        return FoodPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipePreferenceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RecipePreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["recipe", "preference"]
    search_fields = ["recipe__title"]
    ordering_fields = ["preference", "recipe__title"]
    ordering = ["preference"]

    def get_queryset(self):
        return RecipePreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
