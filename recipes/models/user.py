# pylint: disable=no-member

from django.db import models
from django.contrib.auth.models import User
from .base import BaseModel
from .recipe import Ingredient, Recipe, Unit


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    diet_type = models.CharField(max_length=255, blank=True, null=True)
    dietary_restrictions = models.TextField(blank=True, null=True)
    preferences = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.user.username)


class Inventory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.ingredient.name}"

    class Meta:
        verbose_name_plural = "Inventories"


class Feedback(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField()
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title} ({self.rating})"  # type: ignore
