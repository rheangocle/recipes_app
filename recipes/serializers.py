# pylint: disable=no-member

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Recipe,
    Ingredient,
    Category,
    Feedback,
    Tag,
    Inventory,
    UserProfile,
    RecipeIngredient,
    DietType,
    DietaryRestriction,
    FoodPreference,
    FodmapCategory,
    RecipePreference,
    FoodPreference,
    Unit,
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class FodmapCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FodmapCategory
        fields = ["id", "name", "description"]


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "name", "unit_type"]


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

            required_fields = ["name", "quantity", "unit"]
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(
                        f"Each ingredient must have a '{field}' field"
                    )

        return value


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "quantity", "unit"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class UserProfileSerializer(serializers.ModelSerializer):
    diet_type = serializers.PrimaryKeyRelatedField(
        queryset=DietType.objects.all(), many=True, required=False
    )
    dietary_restrictions = serializers.PrimaryKeyRelatedField(
        queryset=DietaryRestriction.objects.all(), many=True, required=False
    )
    preferences = serializers.PrimaryKeyRelatedField(
        queryset=FoodPreference.objects.all(), many=True, required=False
    )

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


class DietTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietType
        fields = ["id", "name"]


class DietaryRestrictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryRestriction
        fields = ["id", "name"]


class FoodPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodPreference
        fields = ["id", "name"]
