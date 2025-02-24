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

    filterset_fields = ["category__id"]

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

    filterset_fields = ["tags", "cuisine"]

    search_fields = ["title"]

    ordering_fields = ["created_at", "title", "total_time"]
    ordering = ["-created_at"]


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


class InventoryViewSet(BaseViewSet):
    serializer_class = InventorySerializer
    # permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["ingredient__name", "quantity"]

    search_fields = ["ingredient__name"]

    ordering_fields = ["quantity", "ingredient__name"]
    ordering = ["ingredient__name"]

    def get_queryset(self):
        return Inventory.objects.filter(user=self.request.user)


class FeedbackViewSet(BaseViewSet):
    serializer_class = FeedbackSerializer
    # permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["recipe", "created_at"]

    search_fields = ["recipe__title", "recipe__cuisine", "comments", "rating"]

    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)


class UserProfileViewSet(BaseViewSet):
    serializer_class = UserProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["diet_type"]

    search_fields = ["dietary_restrictions__name", "preferences__name"]

    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
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
    queryset = FoodPreference.objects.all()
    serializer_class = FoodPreferenceSerializer
    permission_classes = [permissions.AllowAny]
