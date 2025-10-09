import json
from recipes.models import Tag
from .policy import compile_policy_for_user


def _constraints_summary_for_prompt(user):
    policy = compile_policy_for_user(user)
    avoid_names = list(
        Tag.objects.filter(id__in=policy.forbidden_tag_ids).values_list("name", flat=True)
    )
    limits = [
        f"{Tag.objects.get(id=tid).name}:{thr}"
        for tid, thr in policy.limits_by_tag_id.items()
        if thr is not None and thr != float("inf")
    ]
    return {
        "protocol": {
            "name": policy.protocol_name or "n/a",
            "phase": policy.protocol_phase or "n/a",
        },
        "diet_types": sorted(policy.diet_type_names),
        "restrictions": sorted(policy.restriction_names),
        "avoid_tags": avoid_names,
        "limit_tags": limits,
    }


def build_generation_prompt(user, ingredients, cuisine, schema_json):
    c = _constraints_summary_for_prompt(user)
    schema_str = json.dumps(schema_json, separators=(",", ":"))
    ingredients_str = ", ".join(ingredients or [])

    return f"""
You are a culinary generator. Obey ALL policy rules that are data-driven:
- Protocol: {c["protocol"]["name"]} (phase: {c["protocol"]["phase"]})
- Diet types: {", ".join(c["diet_types"]) or "none"}
- Restrictions: {", ".join(c["restrictions"]) or "none"}
- Avoid any ingredient carrying ANY of these tags: {", ".join(c["avoid_tags"]) or "none"}
- Respect LIMIT tags (tag:threshold per serving): {", ".join(c["limit_tags"]) or "none"}.

Output exactly one JSON object that validates against this JSON Schema (no markdown):
{schema_str}

User ingredients (you may add/swap to satisfy policy): {ingredients_str}
Cuisine preference: {cuisine or 'any'}.
""".strip()


def build_repair_prompt(user, recipe_json):
    c = _constraints_summary_for_prompt(user)
    return f"""
Fix the following JSON so it obeys the current policy:
- Avoid tags: {", ".join(c["avoid_tags"]) or "none"}
- Respect LIMIT tags: {", ".join(c["limit_tags"]) or "none"}

Only modify ingredients/notes. Keep all keys. Return ONLY JSON (no markdown).

{json.dumps(recipe_json, separators=(",", ":"))}
""".strip()
