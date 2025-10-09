from typing import Optional
from django.db.models.functions import Lower
from recipes.models import Ingredient, IngredientAlias

def resolve_ingredient_name(name:str) -> Optional[Ingredient]:
    n = (name or "").strip()
    if not n:
        return None
    
    alias = IngredientAlias.objects.filter(name__iexact=n).select_related('ingredient').first()
    if alias:
        return alias.ingredient
    
    return Ingredient.objects.filter(name__iexact=n).first()
    