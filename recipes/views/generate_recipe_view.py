from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import re
import logging
from django.core.exceptions import ValidationError
from ..models import (
    Recipe,
    Ingredient,
    RecipeIngredient,
    Unit,
    UserProfile,
    FodmapCategory,
    FoodPreference,
)
from jsonschema import validate, ValidationError as JSONSchemaValidationError


logger = logging.getLogger(__name__)

RECIPE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "instructions": {"type": "string"},
        "cuisine": {"type": "string"},
        "prep_time": {"type": "integer"},
        "cook_time": {"type": "integer"},
        "total_time": {"type": "integer"},
        "servings": {"type": "integer"},
        "ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "quantity": {"type": "string"},
                    "unit": {"type": "string"}
                },
                "required": ["name", "quantity", "unit"]
            }
        },
        "fodmap_friendly": {"type": "boolean"},
        "fodmap_notes": {"type": "string"}
    },
    "required": ["title", "instructions", "ingredients"]
}

class FODMAPRecipeGeneratorView(APIView):
    api_url = "http://localhost:11434/api/generate"
    model = "deepseek-coder:1.3b"
    
    def validate_ingredients(self, ingredients):
        """Validate ingredient list"""
        MAX_NUM_INGREDIENTS = 25
        if not ingredients:
            raise ValidationError('At least one ingredient is required')
        
        valid_ingredients = list(set([ingredient.strip() for ingredient in ingredients if ingredient.strip()]))
        if not valid_ingredients:
            raise ValidationError('Please provide valid ingredient name')
        
        if len(valid_ingredients) > MAX_NUM_INGREDIENTS:
            raise ValidationError('Maximum 25 ingredients allowed')
        return valid_ingredients
    
    def extract_json_from_response(self, response_text):
        """Extract JSON from markdown response."""
        match = re.search(r"```(?:json)?\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            return match.group(1)

        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            return match.group(0)

        return response_text

    def clean_recipe_data(self, recipe_data):
        """Clean up recipe data types and ensure required fields."""
        for time_field in ["prep_time", "cook_time", "total_time"]:
            if isinstance(recipe_data.get(time_field), str):
                match = re.search(r"\d+", recipe_data[time_field])
                recipe_data[time_field] = int(match.group()) if match else 0

        if "ingredients" not in recipe_data:
            recipe_data["ingredients"] = []

        if "fodmap_friendly" not in recipe_data:
            recipe_data["fodmap_friendly"] = True

        if "fodmap_notes" not in recipe_data:
            recipe_data["fodmap_notes"] = ""

        return recipe_data

    def save_recipe(self, recipe_data):
        """Save recipe to database. Returns saved Recipe object."""

        ingredients = recipe_data.pop("ingredients", [])
        recipe, created = Recipe.objects.update_or_create(
            title=recipe_data["title"],
            defaults={
                "description": recipe_data.get("description", ""),
                "instructions": recipe_data.get("instructions", ""),
                "cuisine": recipe_data.get("cuisine", ""),
                "prep_time": recipe_data.get("prep_time", 0),
                "cook_time": recipe_data.get("cook_time", 0),
                "total_time": recipe_data.get("total_time", 0),
                "servings": recipe_data.get("servings", 2),
                "fodmap_friendly": recipe_data.get("fodmap_friendly", True),
                "fodmap_notes": recipe_data.get("fodmap_notes", ""),
            },
        )

        recipe.ingredients.clear()

        for detail in ingredients:
            if isinstance(detail, dict):
                name = detail.get("name", "").strip()
                quantity = detail.get("quantity", "").strip()
                unit_name = detail.get("unit", "").strip()
            else:
                parts = detail.split(":", 1)
                name = parts[0].strip() if parts else ""
                quantity_unit = parts[1].strip() if len(parts) > 1 else ""

                quantity_match = re.search(r"^([\d./]+)\s*(.*)$", quantity_unit)
                if quantity_match:
                    quantity = quantity_match.group(1)
                    unit_name = quantity_match.group(2)
                else:
                    quantity = quantity_unit
                    unit_name = ""

            if name:
                ingredient, _ = Ingredient.objects.get_or_create(name=name)
                unit = None
                if unit_name:
                    try:
                        unit = Unit.objects.get(name__iexact=unit_name)
                    except Unit.DoesNotExist:
                        pass

                if not ingredient.fodmap_category:
                    try:
                        low_fodmap = FodmapCategory.objects.get(name="Low")
                        ingredient.fodmap_category = low_fodmap
                        ingredient.save()
                    except FodmapCategory.DoesNotExist:
                        pass

                RecipeIngredient.objects.create(
                    recipe=recipe, ingredient=ingredient, quantity=quantity, unit=unit
                )
        return recipe

    def get_user_preferences(self, user):
        if not user or user.is_anonymous:
            return "", []

        try:
            profile = UserProfile.objects.get(user=user)
            diet_type = profile.diet_type.name if profile.diet_type else "Low FODMAP"

            restrictions = list(
                profile.dietary_restrictions.all().values_list("name", flat=True)
            )

            liked_ingredients = list(
                FoodPreference.objects.filter(user=user, preference="like").values_list(
                    "ingredient_name", flat=True
                )
            )

            disliked_ingredients = list(
                FoodPreference.objects.filter(
                    user=user, preference="dislike"
                ).values_list("ingredient_name", flat=True)
            )

            allergic_ingredients = list(
                FoodPreference.objects.filter(
                    user=user, preference="allergic"
                ).values_list("ingredient_name", flat=True)
            )

            preferences = f"Diet type: {diet_type}. "
            if restrictions:
                preferences += f"Dietary restrictions: {', '.join(restrictions)}. "
            if liked_ingredients:
                preferences += f"Likes: {', '.join(liked_ingredients)}. "
            if disliked_ingredients:
                preferences += f"Dislikes: {', '.join(disliked_ingredients)}. "
            if allergic_ingredients:
                preferences += f"Allergies: {', '.join(allergic_ingredients)}. "

            return preferences, allergic_ingredients
        except UserProfile.DoesNotExist:
            return "", []

    @method_decorator(ratelimit(key='user', rate='10/h', method='POST'))
    def post(self, request):
        if getattr(request, 'limited', False):
            return Response(
                {
                    'error': 'Rate limit exceeded. Up to 10 recipes can be generated per hour.'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        try:
            ingredients = request.data.get("ingredients", [])
            preferences = request.data.get("preferences", "")
            dietary_restrictions = request.data.get(
                "dietary_restrictions", "Low FODMAP"
            )
            cuisine = request.data.get("cuisine", "")
            save_recipe = request.data.get("save", False)

            user_preferences, allergic_ingredients = self.get_user_preferences(
                request.user
            )

            if user_preferences and not preferences:
                preferences = user_preferences
            elif user_preferences:
                preferences = f"{preferences}. {user_preferences}"
            # Build prompt
            fodmap_instruction = """
            You are a FODMAP-specialized chef. Create a low FODMAP recipe safe for IBS.
            Follow these FODMAP rules strictly:
            1. Avoid high FODMAP ingredients like onion, garlic, wheat, high-lactose dairy, and certain fruits/vegetables.
            2. Use suitable substitutes (e.g., garlic-infused oil instead of garlic, green parts of spring onion instead of onion).
            3. Include specific portion sizes as FODMAP tolerance depends on serving size.
            4. Include FODMAP-specific notes for any ingredients that need special preparation or consideration.
            """
            
            prompt = (
            f"{fodmap_instruction}\n\n"
            f"Ingredients: {', '.join(ingredients)}.\n"
            f"Preferences: {preferences}.\nCuisine: {cuisine}.\n"
            f"Dietary restrictions: {dietary_restrictions}.\n"
            f"{f'Allergens to avoid: {", ".join(allergic_ingredients)}.' if allergic_ingredients else ''}\n\n"
            "Respond ONLY in valid JSON matching the provided schema exactly."
        )

            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()

            llm_response = response.json().get("response", "")
            json_content = self.extract_json_from_response(llm_response)

            try:
                recipe_data = json.loads(json_content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {str(e)} | Raw response: {llm_response}")
                return Response(
                    {"error": f"Failed to parse recipe JSON: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            recipe_data = self.clean_recipe_data(recipe_data)
            
            try:
                validate(instance=recipe_data, schema=self.RECIPE_JSON_SCHEMA)
            except JSONSchemaValidationError as e:
                logger.error(f"Schema validation error: {e.message}")
                return Response(
                    {"error": f"Recipe validation error: {e.message}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if save_recipe:
                saved_recipe = self.save_recipe(recipe_data)
                return Response(
                    {
                        "message": "Recipe saved successfully",
                        "recipe_id": saved_recipe.id
                    },
                    status=status.HTTP_200_OK
                )
            return Response(recipe_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"POST for AI generation failed: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # def extract_recipe_with_regex(self, text):
    #     recipe_data = {
    #         "title": "",
    #         "description": "",
    #         "instructions": "",
    #         "cuisine": "",
    #         "prep_time": 0,
    #         "cook_time":0,
    #         "total_time": 0,
    #         "servings": 2,
    #         "ingredients": [],
    #         "fodmap_friendly": True,
    #         "fodmap_notes": ""
    #     }
    #            # Extract title
    #     title_match = re.search(r"title[\"']?\s*:\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
    #     if title_match:
    #         recipe_data["title"] = title_match.group(1)
            
    #     # Extract description
    #     desc_match = re.search(r"description[\"']?\s*:\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
    #     if desc_match:
    #         recipe_data["description"] = desc_match.group(1)
            
    #     # Extract instructions
    #     instr_match = re.search(r"instructions[\"']?\s*:\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
    #     if instr_match:
    #         recipe_data["instructions"] = instr_match.group(1)
            
    #     # Extract cuisine
    #     cuisine_match = re.search(r"cuisine[\"']?\s*:\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
    #     if cuisine_match:
    #         recipe_data["cuisine"] = cuisine_match.group(1)
            
    #     # Extract times
    #     prep_match = re.search(r"prep_time[\"']?\s*:\s*(\d+)", text, re.IGNORECASE)
    #     if prep_match:
    #         recipe_data["prep_time"] = int(prep_match.group(1))
            
    #     cook_match = re.search(r"cook_time[\"']?\s*:\s*(\d+)", text, re.IGNORECASE)
    #     if cook_match:
    #         recipe_data["cook_time"] = int(cook_match.group(1))
            
    #     total_match = re.search(r"total_time[\"']?\s*:\s*(\d+)", text, re.IGNORECASE)
    #     if total_match:
    #         recipe_data["total_time"] = int(total_match.group(1))
            
    #     # Extract servings
    #     servings_match = re.search(r"servings[\"']?\s*:\s*(\d+)", text, re.IGNORECASE)
    #     if servings_match:
    #         recipe_data["servings"] = int(servings_match.group(1))
            
    #     # Extract fodmap notes
    #     notes_match = re.search(r"fodmap_notes[\"']?\s*:\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
    #     if notes_match:
    #         recipe_data["fodmap_notes"] = notes_match.group(1)
            
    #     # Try to extract ingredients
    #     ingredients_section = re.search(r"ingredients[\"']?\s*:\s*\[(.*?)\]", text, re.DOTALL)
    #     if ingredients_section:
    #         ingredient_items = re.findall(r"\{(.*?)\}", ingredients_section.group(1), re.DOTALL)
    #         for item in ingredient_items:
    #             ingredient = {}
                
    #             name_match = re.search(r"name[\"']?\s*:\s*[\"']([^\"']+)[\"']", item)
    #             if name_match:
    #                 ingredient["name"] = name_match.group(1)
                    
    #             quantity_match = re.search(r"quantity[\"']?\s*:\s*[\"']([^\"']+)[\"']", item)
    #             if quantity_match:
    #                 ingredient["quantity"] = quantity_match.group(1)
                    
    #             unit_match = re.search(r"unit[\"']?\s*:\s*[\"']([^\"']+)[\"']", item)
    #             if unit_match:
    #                 ingredient["unit"] = unit_match.group(1)
                    
    #             if ingredient.get("name"):
    #                 recipe_data["ingredients"].append(ingredient)
        
    #     return recipe_data
