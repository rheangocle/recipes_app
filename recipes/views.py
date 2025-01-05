from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Recipe, Ingredient, Tag, Inventory, Feedback, Category, UserProfile
from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer, InventorySerializer, FeedbackSerializer, CategorySerializer, UserProfileSerializer


class Pagination(PageNumberPagination):
    page_size = 10


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['category__id']
    
    search_fields = ['name']
    
    ordering_fields = ['name', 'category__name']
    ordering = ['name']
    
    pagination_class = Pagination
    
    
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    
    filterset_fields = ['tags', 'cuisine']
    
    search_fields = ['title']
    
    ordering_fields = ['created_at', 'title', 'total_time']
    ordering = ['-created_at']
    
    pagination_class = Pagination
    
    
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['name']
    
    search_fields = ['name']
    
    ordering_fields = ['name']
    ordering = ['name']
    
    pagination_class = Pagination
    
    
class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['ingredient__name', 'quantity']
    
    search_fields = ['ingredient__name']
    
    ordering_fields = ['quantity', 'ingredient__name']
    ordering = ['ingredient__name']
    
    pagination_class = Pagination
    
    def get_queryset(self):
        return Inventory.objects.filter(user=self.request.user)
    
    
class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['recipe', 'created_at']
    
    search_fields = ['recipe__title', 'recipe__cuisine', 'comments', 'rating']
    
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    pagination_class = Pagination
    
    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)
    

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [permissions.IsAdminUser]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['name']
    
    search_fields = ['name']
    
    ordering_fields = ['name']
    
    pagination_class = Pagination
    
    
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['diet_type']
    
    search_fields = ['dietary_restrictions', 'preferences']
    
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    
    