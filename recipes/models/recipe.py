# pylint: disable=no-member

from django.db import models
from .base import BaseModel
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Q
from django.db.models.functions import Lower
User = get_user_model()

class Category(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Categories"


class Unit(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    unit_type = models.CharField(
        max_length=50,
        choices=[("weight", "Weight"), ("volume", "Volume"), ("count", "Count")],
    )

    def __str__(self):
        return str(self.name)

class Ingredient(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='ingredients'
    )
    default_unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL, blank=True, null=True
    )
    fodmap_category = models.ForeignKey('FodmapCategory', on_delete=models.SET_NULL, null=True, blank=True)
    substitutes = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='substitute_for')
    nutritional_info = models.JSONField(null=True, blank=True)
    tags=models.ManyToManyField('Tag', blank=True, related_name='ingredients')

    def __str__(self):
        return str(self.name)

class IngredientAlias(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='aliases')

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('name'), name='uniq_ingredientalias_name_ci')
        ]
    
    def __str__(self):
        return f"{self.name} -> {self.ingredient.name}"

class Tag(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.name)

    
class Recipe(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField()
    cuisine = models.CharField(max_length=100, blank=True, null=True, default="")
    prep_time = models.IntegerField(default=0)
    cook_time = models.IntegerField(default=0)
    total_time = models.IntegerField(default=0)
    servings = models.IntegerField(default=2)
    ingredients = models.ManyToManyField(Ingredient, through="RecipeIngredient")
    tags = models.ManyToManyField("Tag", blank=True)
    image = models.ImageField(upload_to='recipe_images/', null=True, blank=True)
    fodmap_friendly = models.BooleanField(default=True)
    fodmap_notes = models.TextField(blank=True, help_text='Notes about FODMAP considerations for this recipe')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_recipes'
    )

    def __str__(self):
        return str(self.title)


class RecipeIngredient(BaseModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50)
    unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.quantity} {self.unit} {self.ingredient.name} in {self.recipe.title}"

class FodmapCategory(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'FODMAP Categories'
     