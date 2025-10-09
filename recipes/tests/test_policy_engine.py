from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Tag, Ingredient, DietType, DietaryRestriction, UserProfile
from ..models.policy import (
    DietTypeRule,
    DietProtocol,
    DietProtocolRule,
    UserProtocol,
    ProtocolPhase,
)
from ..policy.policy import compile_policy_for_user
from ..policy.validation import check_recipe_against_policy
from ..models.base import BaseModel

User = get_user_model()


class PolicyEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="x")
        self.profile = UserProfile.objects.get(user=self.user)

        # Tags
        self.t_meat = Tag.objects.create(name="meat")
        self.t_pork = Tag.objects.create(name="pork")
        self.t_alcohol = Tag.objects.create(name="alcohol")
        self.t_fodmap_high = Tag.objects.create(name="fodmap-high")

        # Diet types & rules
        self.veg, _ = DietType.objects.get_or_create(name="Vegetarian")
        DietTypeRule.objects.get_or_create(diet_type=self.veg, tag=self.t_meat, defaults={"rule": DietTypeRule.Rule.AVOID})

        self.halal, _ = DietType.objects.get_or_create(name="Halal")
        DietTypeRule.objects.get_or_create(diet_type=self.halal, tag=self.t_pork, defaults={"rule": DietTypeRule.Rule.AVOID})
        DietTypeRule.objects.get_or_create(
            diet_type=self.halal, tag=self.t_alcohol, defaults={"rule": DietTypeRule.Rule.AVOID}
        )

        self.profile.diet_types.add(self.veg, self.halal)

        # Protocol
        self.proto, _ = DietProtocol.objects.get_or_create(name="Low-FODMAP")
        DietProtocolRule.objects.get_or_create(
            protocol=self.proto,
            tag=self.t_fodmap_high,
            phase=ProtocolPhase.ELIMINATION,
            defaults={"rule": DietProtocolRule.Rule.AVOID},
        )
        UserProtocol.objects.create(
            user=self.user,
            protocol=self.proto,
            phase=ProtocolPhase.ELIMINATION,
            is_primary=True,
        )

        # Ingredients
        self.ing_bacon = Ingredient.objects.create(name="Bacon")
        self.ing_bacon.tags.add(self.t_meat, self.t_pork)

        self.ing_wine = Ingredient.objects.create(name="Red Wine")
        self.ing_wine.tags.add(self.t_alcohol)

        self.ing_onion = Ingredient.objects.create(name="Onion")
        self.ing_onion.tags.add(self.t_fodmap_high)

    def test_compile_policy(self):
        p = compile_policy_for_user(self.user)
        self.assertIn(self.t_meat.id, p.forbidden_tag_ids)
        self.assertIn(self.t_pork.id, p.forbidden_tag_ids)
        self.assertIn(self.t_alcohol.id, p.forbidden_tag_ids)
        self.assertIn(self.t_fodmap_high.id, p.forbidden_tag_ids)
        self.assertEqual(p.protocol_name, "Low-FODMAP")
        self.assertEqual(p.protocol_phase, ProtocolPhase.ELIMINATION)

    def test_validation_blocks_forbidden_tags(self):
        recipe = {
            "title": "Bad Breakfast",
            "instructions": "Cook it.",
            "ingredients": [
                {"name": "Bacon", "quantity": "50", "unit": "g"},
                {"name": "Red Wine", "quantity": "10", "unit": "ml"},
                {"name": "Onion", "quantity": "20", "unit": "g"},
            ],
        }
        v = check_recipe_against_policy(self.user, recipe)
        self.assertTrue(any("tags" in msg and "Bacon" in msg for msg in v))
        self.assertTrue(any("tags" in msg and "Red Wine" in msg for msg in v))
        self.assertTrue(any("tags" in msg and "Onion" in msg for msg in v))
