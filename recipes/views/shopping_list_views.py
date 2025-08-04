from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from ..models import Recipe, RecipeIngredient
import re


class ShoppingListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create shopping list from recipe IDs"""
        recipe_ids = request.data.get("recipe_ids", [])
        if not recipe_ids:
            return Response(
                {"error": "No recipe IDs provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        ingredients = (
            RecipeIngredient.objects.filter(recipe_id__in=recipe_ids)
            .select_related("ingredient", "unit")
            .values(
                "ingredient__name",
                "ingredient__id",
                "unit__name",
                "quantity",
                "recipe__title",
            )
        )

        shopping_list = {}
        for item in ingredients:
            key = f"{item['ingredient__name']}_{item['unit__name'] or 'unit'}"

            if key not in shopping_list:
                shopping_list[key] = {
                    "ingredient_id": item["ingredient__id"],
                    "ingredient": item["ingredient__name"],
                    "unit": item["unit__name"],
                    "quantities": [],
                    "recipes": [],
                }
            shopping_list[key]["quantities"].append(item["quantity"])
            shopping_list[key]["recipes"].append(item["recipe__title"])

        from ..models import Inventory

        inventory_items = Inventory.objects.filter(
            user=request.user,
            ingredient__in=[item["ingredient_id"] for item in shopping_list.values()],
        ).values("ingredient__id", "quantity", "unit__name")

        inventory_map = {item["ingredient__id"]: item for item in inventory_items}

        final_list = []
        for item in shopping_list.values():
            in_inventory = inventory_map.get(item["ingredient_id"])

            final_list.append(
                {
                    "ingredient": item["ingredient"],
                    "unit": item["unit"],
                    "quantity": item["quantity"],
                    "total_quantity": self._sum_quantities(item["quantities"]),
                    "recipes": list(set(item["recipes"])),
                    "in_inventory": bool(in_inventory),
                    "inventory_quantity": (
                        in_inventory["quantity"] if in_inventory else 0
                    ),
                    "inventory_unit": (
                        in_inventory["unit__name"] if in_inventory else None
                    ),
                }
            )
        return Response(
            {
                "shopping_list": final_list,
                "total_items": len(final_list),
                "recipe_count": len(recipe_ids),
            }
        )

    def _sum_quantities(self, quantities):
        """Try to sum quantities"""
        total = 0
        for q in quantities:
            try:
                match = re.search(r"([\d.]+)", str(q))
                if match:
                    total += float(match.group(1))
            except:
                pass
        return total if total > 0 else "Multiple"
