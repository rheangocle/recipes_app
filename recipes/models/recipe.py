# pylint: disable=no-member

from django.db import models
from .base import BaseModel


class Recipe(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField()
    cuisine = models.CharField(max_length=100, blank=True, null=True, default="")
    prep_time = models.IntegerField()
    cook_time = models.IntegerField()
    total_time = models.IntegerField()

    # ingredients = models.JSONField(default=dict)
    ingredients = models.ManyToManyField("Ingredient", through="RecipeIngredient")
    tags = models.ManyToManyField("Tag", blank=True)

    def __str__(self):
        return str(self.title)


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
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    default_unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return str(self.name)

class RecipeIngredient(BaseModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50)
    unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL, null=True, blank=True
    )
    
    def __str__(self):
        return f"{self.quantity} {self.ingredient.name} in {self.recipe.title}"

class Tag(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.name)
