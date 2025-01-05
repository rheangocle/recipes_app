from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recipe, Ingredient
from .serializers import RecipeSerializer, IngredientSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all() # pylint: disable=no-member
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all() # pylint: disable=no-member
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tags', 'cuisine']