from typing import List
import re
from recipes.models import Tag
from .policy import compile_policy_for_user
from .ingredients import resolve_ingredient_name

_NUM = re.compile(r"(\d+(?:\.\d+)?)")

def _parse_float(s:str):
    m = _NUM.search(s)
    return float(m.group(1)) if m else None

def check_recipe_against_policy(user, recipe) -> List[str]:
    policy = compile_policy_for_user(user)
    violations : List[str] = []

    for item in recipe.get('ingredients', []):
        iname = (item.get('name') or "").strip()
        ing = resolve_ingredient_name(iname)
        if not ing:
            violations.append(f"Unknown ingredient: {iname}")
            continue
        
        if ing.id in policy.forbidden_ingredient_ids:
            violations.append(f"Restricton violation: {iname}")
            continue
        
        ing_tag_ids = set(ing.tags.values_list('id', flat=True))
        banned = ing_tag_ids & policy.forbidden_tag_ids
        if banned:
            tag_names = ', '.join(Tag.objects.filter(id__in=banned).values_list('name', flat=True))
            violations.append(f"Policy violation: {iname} is forbidden because it contains tags: {tag_names}")
            
    return violations