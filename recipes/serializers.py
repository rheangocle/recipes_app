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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class IngredientSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    fodmap_category = FodmapCategorySerializer(read_only=True)
    default_unit = UnitSerializer(read_only=True)

    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "category",
            "default_unit",
            "fodmap_category",
            "nutritional_info",
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ["id", "ingredient", "quantity", "unit", "notes"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "description"]


class RecipeSerializer(serializers.ModelSerializer):
    ingredients_detail = RecipeIngredientSerializer(
        source="recipeingredient_set", many=True, read_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source="tags",
        write_only=True,
        many=True,
        required=False,
    )
    ingredients_data = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )
    
    def validate_title(self, value):
        if len(value) < 1:
            raise serializers.ValidationError('Title must be at least 1 character long')
        return value

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "description",
            "ingredients_detail",
            "ingredients_data",
            "instructions",
            "prep_time",
            "cook_time",
            "total_time",
            "servings",
            "cuisine",
            "tags",
            "tag_ids",
            "fodmap_friendly",
            "fodmap_notes",
            "image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients_data", [])
        tags = validated_data.pop("tags", [])

        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)

        for ingredient_data in ingredients_data:
            ingredient_name = ingredient_data.get("ingredient_name")
            quantity = ingredient_data.get("quantity")
            unit_id = ingredient_data.get("unit_id")

            ingredient, _ = Ingredient.objects.get_or_create(name=ingredient_name)
            unit = Unit.objects.get(id=unit_id) if unit_id else None
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity=quantity,
                unit=unit,
                notes=ingredient_data.get("notes", ""),
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients_data", None)
        tags = validated_data.pop("tags", None)

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            for ingredient_data in ingredients_data:
                ingredient_name = ingredient_data.get("ingredient_name")
                quantity = ingredient_data.get("quantity")
                unit_id = ingredient_data.get("unit_id")

                ingredient, _ = Ingredient.objects.get_or_create(name=ingredient_name)
                unit = Unit.objects.get(id=unit_id) if unit_id else None
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    quantity=quantity,
                    unit=unit,
                    notes=ingredient_data.get("notes", ""),
                )
        return instance

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


class DietTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietType
        fields = ["id", "name", "description"]


class DietaryRestrictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryRestriction
        fields = ["id", "name", "description"]


class UserProfileSerializer(serializers.ModelSerializer):
    diet_type = DietTypeSerializer(read_only=True)
    diet_type_id = serializers.PrimaryKeyRelatedField(
        queryset=DietType.objects.all(),
        source="diet_type",
        write_only=True,
        required=False,
        allow_null=True,
    )
    dietary_restrictions = DietaryRestrictionSerializer(many=True, read_only=True)
    dietary_restriction_ids = serializers.PrimaryKeyRelatedField(
        queryset=DietaryRestriction.objects.all(),
        source="dietary_restrictions",
        write_only=True,
        many=True,
        required=False,
    )
    food_preferences = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "diet_type",
            "diet_type_ids",
            "dietary_restrictions",
            "dietary_restriction_ids",
            "food_preferences",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def get_food_preferences(self, obj):
        preferences = FoodPreference.objects.filter(user=obj.user)
        return FoodPreferenceSerializer(preferences, many=True).data


class FeedbackSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = [
            "id",
            "user",
            "recipe",
            "rating",
            "comments",
            "created_at",
            "user_profile",
        ]
        read_only_fields = ["created_at"]

    def get_user_profile(self, obj):
        try:
            return UserProfileSerializer(obj.user.profile).data
        except UserProfile.DoesNotExist:
            return None


class InventorySerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient", write_only=True
    )

    unit = UnitSerializer(read_only=True)
    unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        source="unit",
        write_only=True,
        required=False,
        allow_null=True,
    )

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value

    class Meta:
        model = Inventory
        fields = ["id", "user", "ingredient", "quantity", "unit"]


class FoodPreferenceSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient", write_only=True
    )

    class Meta:
        model = FoodPreference
        fields = ["id", "ingredient", "ingredient_id", "preference"]
        read_only_fields = ["user"]


class RecipePreferenceSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)
    recipe_id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), source="recipe", write_only=True
    )

    class Meta:
        model = RecipePreference
        fields = ["id", "user", "recipe", "recipe_id", "preference"]
        read_only_fields = ["user"]
