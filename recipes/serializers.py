from rest_framework import serializers
from .models import Recipe, Ingredient, RecipeIngredient, Category, Feedback, Tag, Inventory, UserProfile


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        
class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'ingredients', 'instructions', 'prep_time', 'cook_time', 'total_time', 'tags']

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()
    
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'unit']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'  
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'diet_type', 'dietary_restrictions', 'preferences']
        read_only_fields = ['user']
        
class FeedbackSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='user.userprofile')
    
    class Meta:
        model = Feedback
        fields = ['user', 'recipe', 'rating', 'comments', 'created_at']
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'description']
        
class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['user', 'ingredient', 'quantity', 'unit']
        
