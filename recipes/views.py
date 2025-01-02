from django.shortcuts import render
from rest_framework import viewsets
from .models import Recipe, Ingredient
from .serializers import RecipeSerializer, IngredientSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all() # pylint: disable=no-member
    serializer_class = IngredientSerializer
    
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all() # pylint: disable=no-member
    serializer_class = RecipeSerializer