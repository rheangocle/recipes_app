from rest_framework import serializers
from .models import (
    Recipe,
    Ingredient,
    Category,
    Feedback,
    Tag,
    Inventory,
    UserProfile,
)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "description",
            "ingredients",
            "instructions",
            "prep_time",
            "cook_time",
            "total_time",
            "cuisine",
            "tags",
        ]
        
    def validate_ingredients(self, value):
        """Validate ingredients structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Ingredients must be a list")
                
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each ingredient must be an object")
                    
            required_fields = ['name', 'quantity', 'unit']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Each ingredient must have a '{field}' field")
                    
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "user", "diet_type", "dietary_restrictions", "preferences"]
        read_only_fields = ["user"]


class FeedbackSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source="user.userprofile")

    class Meta:
        model = Feedback
        fields = ["user", "recipe", "rating", "comments", "created_at"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name", "description"]


class InventorySerializer(serializers.ModelSerializer):
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value

    class Meta:
        model = Inventory
        fields = ["user", "ingredient", "quantity", "unit"]
