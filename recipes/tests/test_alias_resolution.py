from django.test import TestCase
from ..models import Ingredient, IngredientAlias
from ..policy.ingredients import resolve_ingredient_name


class AliasResolutionTests(TestCase):
    def test_alias(self):
        ing = Ingredient.objects.create(name="Green Onion Tops")
        IngredientAlias.objects.create(name="Scallion Tops", ingredient=ing)

        r = resolve_ingredient_name("scallion tops")
        self.assertEqual(r.id, ing.id)
