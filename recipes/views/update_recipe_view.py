from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import re
from recipes.models import (
    Recipe, 
    Ingredient, 
    RecipeIngredient, 
    UserProfile, 
    FoodPreference,
    Unit
)

class UpdateFODMAPRecipeView(APIView):
    """View for updating FODMAP-friendly recipes"""
    api_url = "http://localhost:11434/api/generate"
    model = "llama3.2:1b"

    def extract_json_from_response(self, response_text):
        """Extract JSON from markdown response."""
        match = re.search(r"```(?:json)?\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            return match.group(1)
        
        # Try with just curly braces if markdown code block not found
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            return match.group(0)
            
        return response_text

    def clean_recipe_data(self, recipe_data):
        """Clean up recipe data types and ensure required fields."""
        # Convert string time values to integers
        for time_field in ["prep_time", "cook_time", "total_time"]:
            if isinstance(recipe_data.get(time_field), str):
                match = re.search(r"\d+", recipe_data[time_field])
                recipe_data[time_field] = int(match.group()) if match else 0
        
        # Ensure ingredients array exists
        if "ingredients" not in recipe_data:
            recipe_data["ingredients"] = []
            
        # Add FODMAP specific fields if missing
        if "fodmap_friendly" not in recipe_data:
            recipe_data["fodmap_friendly"] = True
            
        if "fodmap_notes" not in recipe_data:
            recipe_data["fodmap_notes"] = ""
            
        return recipe_data

    def save_recipe(self, recipe_data, recipe):
        """Save recipe to database. Returns saved Recipe object."""
        
        ingredients = recipe_data.pop("ingredients", [])
        
        # Update recipe fields
        recipe.title = recipe_data.get("title", recipe.title)
        recipe.description = recipe_data.get("description", recipe.description)
        recipe.instructions = recipe_data.get("instructions", recipe.instructions)
        recipe.cuisine = recipe_data.get("cuisine", recipe.cuisine)
        recipe.prep_time = recipe_data.get("prep_time", recipe.prep_time)
        recipe.cook_time = recipe_data.get("cook_time", recipe.cook_time)
        recipe.total_time = recipe_data.get("total_time", recipe.total_time)
        recipe.servings = recipe_data.get("servings", recipe.servings)
        recipe.fodmap_friendly = recipe_data.get("fodmap_friendly", recipe.fodmap_friendly)
        recipe.fodmap_notes = recipe_data.get("fodmap_notes", recipe.fodmap_notes)
        recipe.save()
        
        # Clear existing ingredients
        recipe.ingredients.clear()
        
        # Add ingredients
        for detail in ingredients:
            # Handle different incoming formats
            if isinstance(detail, dict):
                name = detail.get("name", "").strip()
                quantity = detail.get("quantity", "").strip()
                unit_name = detail.get("unit", "").strip()
            else:
                # Try to parse string format "ingredient: amount"
                parts = detail.split(":", 1)
                name = parts[0].strip() if parts else ""
                quantity_unit = parts[1].strip() if len(parts) > 1 else ""
                
                # Try to separate quantity and unit
                quantity_match = re.search(r"^([\d./]+)\s*(.*)$", quantity_unit)
                if quantity_match:
                    quantity = quantity_match.group(1)
                    unit_name = quantity_match.group(2)
                else:
                    quantity = quantity_unit
                    unit_name = ""
            
            if name:
                # Get or create ingredient
                ingredient, _ = Ingredient.objects.get_or_create(name=name)
                
                # Try to get unit
                unit = None
                if unit_name:
                    try:
                        unit = Unit.objects.get(name__iexact=unit_name)
                    except Unit.DoesNotExist:
                        pass
                
                # Create recipe ingredient relationship
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity=quantity,
                    unit=unit
                )
        
        return recipe

    def get_user_preferences(self, user):
        """Get user preferences for prompting."""
        if not user or user.is_anonymous:
            return "", []
            
        try:
            profile = UserProfile.objects.get(user=user)
            
            diet_type = profile.diet_type.name if profile.diet_type else "Low FODMAP"
            
            # Get dietary restrictions
            restrictions = list(profile.dietary_restrictions.all().values_list('name', flat=True))
            
            # Get ingredient preferences
            liked_ingredients = list(FoodPreference.objects.filter(
                user=user, 
                preference='like'
            ).values_list('ingredient__name', flat=True))
            
            disliked_ingredients = list(FoodPreference.objects.filter(
                user=user, 
                preference='dislike'
            ).values_list('ingredient__name', flat=True))
            
            allergic_ingredients = list(FoodPreference.objects.filter(
                user=user, 
                preference='allergic'
            ).values_list('ingredient__name', flat=True))
            
            # Compile preferences
            preferences = f"Diet type: {diet_type}. "
            if restrictions:
                preferences += f"Dietary restrictions: {', '.join(restrictions)}. "
            if liked_ingredients:
                preferences += f"Likes: {', '.join(liked_ingredients)}. "
            if disliked_ingredients:
                preferences += f"Dislikes: {', '.join(disliked_ingredients)}. "
            if allergic_ingredients:
                preferences += f"Allergic to: {', '.join(allergic_ingredients)}. "
                
            return preferences, allergic_ingredients
                
        except UserProfile.DoesNotExist:
            return "", []

    def post(self, request):
        try:
            # Extract request data
            recipe_id = request.data.get("recipe_id")
            updated_ingredients = request.data.get("ingredients", [])
            preferences = request.data.get("preferences", "")
            dietary_restrictions = request.data.get("dietary_restrictions", "Low FODMAP")
            cuisine = request.data.get("cuisine", "")
            save_recipe = request.data.get("save", False)
            
            if not recipe_id:
                return Response(
                    {"error": "recipe id is required for updating a recipe"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                recipe = Recipe.objects.get(id=recipe_id)
            except Recipe.DoesNotExist:
                return Response(
                    {"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
                )
            
            # Get user preferences if authenticated
            user_preferences, allergic_ingredients = self.get_user_preferences(request.user)
            
            # Combine provided preferences with user preferences
            if user_preferences and not preferences:
                preferences = user_preferences
            elif user_preferences:
                preferences = f"{preferences}. {user_preferences}"
            
            # Add FODMAP specific instruction
            fodmap_instruction = """
            You are a FODMAP-specialized chef. Refine this recipe to be Low FODMAP and safe for people with IBS.
            Follow these FODMAP rules strictly:
            1. Avoid high FODMAP ingredients like onion, garlic, wheat, high-lactose dairy, and certain fruits/vegetables.
            2. Use suitable substitutes (e.g., garlic-infused oil instead of garlic, green parts of spring onion instead of onion).
            3. Include specific portion sizes as FODMAP tolerance depends on serving size.
            4. Include FODMAP-specific notes for any ingredients that need special preparation or consideration.
            """
            
            # Get current ingredients as string
            current_ingredients = ", ".join([
                f"{ri.ingredient.name}: {ri.quantity} {ri.unit.name if ri.unit else ''}" 
                for ri in RecipeIngredient.objects.filter(recipe=recipe)
            ])
            
            # Build prompt
            prompt = (
                f"{fodmap_instruction}\n\n"
                f"Refine this recipe using the following information:\n"
                f"Updated Ingredients: {', '.join(updated_ingredients) if updated_ingredients else current_ingredients}.\n"
                f"Preferences: {preferences}.\n"
                f"Cuisine: {cuisine or recipe.cuisine}.\n"
                f"Dietary Restrictions: {dietary_restrictions}.\n"
                
                # Add warning about allergic ingredients
                f"{f'IMPORTANT: Completely avoid these allergens: {", ".join(allergic_ingredients)}.' if allergic_ingredients else ''}\n\n"
                
                f"Original Recipe:\n"
                f"Title: {recipe.title}\n"
                f"Description: {recipe.description or 'No description provided'}\n"
                f"Instructions: {recipe.instructions}\n"
                f"Prep Time: {recipe.prep_time} minutes\n"
                f"Cook Time: {recipe.cook_time} minutes\n"
                f"Total Time: {recipe.total_time} minutes\n"
                f"Servings: {recipe.servings}\n"
                f"Ingredients: {current_ingredients}\n"
                f"FODMAP Notes: {recipe.fodmap_notes or 'No FODMAP notes provided'}\n\n"
                
                "Return a JSON object with these exact fields:\n"
                "{\n"
                '  "title": string,\n'
                '  "description": string,\n'
                '  "instructions": string,\n'
                '  "cuisine": string,\n'
                '  "prep_time": integer (minutes),\n'
                '  "cook_time": integer (minutes),\n'
                '  "total_time": integer (minutes),\n'
                '  "servings": integer,\n'
                '  "ingredients": [\n'
                '    {\n'
                '      "name": string,\n'
                '      "quantity": string,\n'
                '      "unit": string\n'
                '    }\n'
                '  ],\n'
                '  "fodmap_friendly": boolean,\n'
                '  "fodmap_notes": string\n'
                "}"
            )

            # Call LLM API
            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()

            # Extract and parse response
            llm_response = response.json().get("response", "")
            json_content = self.extract_json_from_response(llm_response)
            
            try:
                recipe_data = json.loads(json_content)
                recipe_data = self.clean_recipe_data(recipe_data)
            except json.JSONDecodeError:
                # Fallback: Try to extract with regex for badly formatted responses
                recipe_data = self.extract_recipe_with_regex(llm_response)
                recipe_data = self.clean_recipe_data(recipe_data)
            
            # Save recipe if requested
            if save_recipe:
                saved_recipe = self.save_recipe(recipe_data, recipe)
                return Response(
                    {
                        "message": "Recipe updated successfully",
                        "recipe_id": saved_recipe.id
                    }, status=status.HTTP_200_OK
                )

            return Response(recipe_data, status=status.HTTP_200_OK)

        except json.JSONDecodeError as e:
            return Response(
                {"error": f"Failed to parse recipe: {str(e)}", "raw_response": llm_response},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def extract_recipe_with_regex(self, text):
        """Fallback method to extract recipe information using regex."""
        recipe_data = {
            "title": "",
            "description": "",
            "instructions": "",
            "cuisine": "",
            "prep_time": 0,
            "cook_time": 0,
            "total_time": 0,
            "servings": 4,
            "ingredients": [],
            "fodmap_friendly": True,
            "fodmap_notes": ""
        }
        
        # Extract title
        title_match = re.search(r"title[\"']?\s*:\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
        if title_match:
            recipe_data["title"] = title_match.group(1)
            
        # Extract description
        desc_match = re.search(r"description[\"']?\s*:\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
        if desc_match:
            recipe_data["description"] = desc_match.group(1)
            
        # Extract instructions
        instr_match = re.search(r"instructions[\"']?\s*:\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
        if instr_match:
            recipe_data["instructions"] = instr_match.group(1)
            
        # Extract cuisine
        cuisine_match = re.search(r"cuisine[\"']?\s*:\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
        if cuisine_match:
            recipe_data["cuisine"] = cuisine_match.group(1)
            
        # Extract times
        prep_match = re.search(r"prep_time[\"']?\s*:\s*(\d+)", text, re.IGNORECASE)
        if prep_match:
            recipe_data["prep_time"] = int(prep_match.group(1))
            
        cook_match = re.search(r"cook_time[\"']?\s*:\s*(\d+)", text, re.IGNORECASE)
        if cook_match:
            recipe_data["cook_time"] = int(cook_match.group(1))
            
        total_match = re.search(r"total_time[\"']?\s*:\s*(\d+)", text, re.IGNORECASE)
        if total_match:
            recipe_data["total_time"] = int(total_match.group(1))
            
        # Extract servings
        servings_match = re.search(r"servings[\"']?\s*:\s*(\d+)", text, re.IGNORECASE)
        if servings_match:
            recipe_data["servings"] = int(servings_match.group(1))
            
        # Extract fodmap notes
        notes_match = re.search(r"fodmap_notes[\"']?\s*:\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
        if notes_match:
            recipe_data["fodmap_notes"] = notes_match.group(1)
            
        # Try to extract ingredients
        ingredients_section = re.search(r"ingredients[\"']?\s*:\s*\[(.*?)\]", text, re.DOTALL)
        if ingredients_section:
            ingredient_items = re.findall(r"\{(.*?)\}", ingredients_section.group(1), re.DOTALL)
            for item in ingredient_items:
                ingredient = {}
                
                name_match = re.search(r"name[\"']?\s*:\s*[\"']([^\"']+)[\"']", item)
                if name_match:
                    ingredient["name"] = name_match.group(1)
                    
                quantity_match = re.search(r"quantity[\"']?\s*:\s*[\"']([^\"']+)[\"']", item)
                if quantity_match:
                    ingredient["quantity"] = quantity_match.group(1)
                    
                unit_match = re.search(r"unit[\"']?\s*:\s*[\"']([^\"']+)[\"']", item)
                if unit_match:
                    ingredient["unit"] = unit_match.group(1)
                    
                if ingredient.get("name"):
                    recipe_data["ingredients"].append(ingredient)
        
        return recipe_data