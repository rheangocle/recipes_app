# pylint: disable=no-member

from django.db import models
from django.contrib.auth.models import User
from .base import BaseModel
from .recipe import Ingredient, Recipe, Unit


class DietType(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class DietaryRestriction(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# class FoodPreference(BaseModel):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name

class Inventory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ({self.ingredient.name} {self.unit})"

    class Meta:
        verbose_name_plural = "Inventories"


class Feedback(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(default=0)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} - {self.recipe.title} ({self.rating})"  # type: ignore


class FoodPreference(BaseModel):
    PREFERENCE_CHOICES = [
        ("like", "Like"),
        ("dislike", "Dislike"),
        ("neutral", "Neutral"),
        ("allergic", "Allergic"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="food_preferences"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    preference = models.CharField(
        max_length=20, choices=PREFERENCE_CHOICES, default="neutral"
    )

    class Meta:
        unique_together = ["user", "ingredient"]

    def __str__(self):
        return f"{self.user.username} - {self.ingredient.name}: {self.preference}"


class RecipePreference(models.Model):
    PREFERENCE_CHOICES = [
        ("like", "Like"),
        ("dislike", "Dislike"),
        ("neutral", "Neutral"),
        ('favorite', 'Favorite')
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipe_preferences"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='user_preferences')
    preference = models.CharField(
        max_length=20, choices=PREFERENCE_CHOICES, default="neutral"
    )

    class Meta:
        unique_together = ["user", "recipe"]

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}: {self.preference}"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    diet_type = models.ForeignKey(DietType, on_delete=models.CASCADE, null=True, blank=True)
    dietary_restrictions = models.ManyToManyField(DietaryRestriction, blank=True)
    preferences = models.ManyToManyField(FoodPreference, blank=True, related_name='user_profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"

