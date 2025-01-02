# pylint: disable=no-member

from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField()
    cuisine = models.CharField(max_length=100, blank=True, null=True)
    prep_time = models.IntegerField()
    cook_time = models.IntegerField()
    total_time = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    ingredients = models.ManyToManyField('Ingredient', through='RecipeIngredient')
    tags = models.ManyToManyField('Tag', blank=True)
    
    def __str__(self):
        return str(self.title)

    
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return str(self.name)
        
    class Meta:
        verbose_name_plural = "Categories"
    
class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    unit_type = models.CharField(max_length=50, choices=[('weight', 'Weight'), ('volume', 'Volume'), ('count', 'Count')])    

    def __str__(self):
        return str(self.name)
    
class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    default_unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.name)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.ingredient.name} in {self.recipe.title}: {self.quantity} {self.unit.name if self.unit else ''}" 
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    diet_type = models.CharField(max_length=255, blank=True, null=True)
    dietary_restrictions = models.TextField(blank=True, null=True)
    preferences = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return str(self.user.username)
    
class Inventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.ingredient.name}"

    class Meta:
        verbose_name_plural = "Inventories"
    

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField()
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.recipe.title} ({self.rating})"
    
class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.name)