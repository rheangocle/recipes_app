from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import re
from recipes.models import Recipe, Ingredient, RecipeIngredient


class UpdateRecipeView(APIView):
    api_url = "http://localhost:11434/api/generate"
    model = "llama3.2:1b"

    def extract_json_from_response(self, response_text):
        """Extract JSON from markdown response."""
        match = re.search(r"```(?:json)?\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            return match.group(1)

        return response_text

    def clean_recipe_data(self, recipe_data):
        """Clean up recipe data types and ensure required fields."""
        for time_field in ["prep_time", "cook_time", "total_time"]:
            if isinstance(recipe_data.get(time_field), str):
                match = re.search(r"\d+", recipe_data[time_field])
                recipe_data[time_field] = int(match.group()) if match else 0

        if "ingredients" not in recipe_data:
            recipe_data["ingredients"] = []

        return recipe_data

    def save_recipe(self, recipe_data, recipe):
        """Save recipe to database. Returns saved Recipe object."""

        ingredients = recipe_data.pop("ingredients", [])

        recipe.title = recipe_data.get("title", recipe.title)
        recipe.description = recipe_data.get("description", recipe.description)
        recipe.instructions = recipe_data.get("instructions", recipe.instructions)
        recipe.cuisine = recipe_data.get("cuisine", recipe.cuisine)
        recipe.prep_time = recipe_data.get("prep_time", recipe.prep_time)
        recipe.cook_time = recipe_data.get("cook_time", recipe.cook_time)
        recipe.total_time = recipe_data.get("total_time", recipe.total_time)
        recipe.save()

        recipe.ingredients.clear()

        for detail in ingredients:
            name = detail.get("name").strip()
            quantity = detail.get("quantity", "").strip()
            unit = detail.get("unit", "").strip()

            if name:
                ingredient, _ = Ingredient.objects.get_or_create(name=name)

                RecipeIngredient.objects.create(
                    recipe=recipe, ingredient=ingredient, quantity=quantity, unit=unit
                )
        return recipe

    def post(self, request):
        try:
            recipe_id = request.data.get("recipe_id")
            updated_ingredients = request.data.get("ingredients", [])
            preferences = request.data.get("preferences", "")
            dietary_restrictions = request.data.get("dietary_restrictions", "")
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

            # Build prompt
            prompt = (
                f"Refine this recipe using the following information:\n"
                f"Updated Ingredients: {', '.join(updated_ingredients)}.\n"
                f"Preferences: {preferences}.\n"
                f"Cuisine: {cuisine}.\n"
                f"Dietary Restrictions: {dietary_restrictions}.\n"
                f"Original Recipe:\n"
                f"Title: {recipe.title}\n"
                f"Description: {recipe.description}\n"
                f"Instructions: {recipe.instructions}\n"
                f"Prep Time: {recipe.prep_time}\n"
                f"Cook Time: {recipe.cook_time}\n"
                f"Total Time: {recipe.total_time}\n"
                f"Ingredients: {', '.join([str(ing.name) for ing in recipe.ingredients.all()])}\n"
                "Return a JSON object with these exact fields:\n"
                "{\n"
                '  "title": string,\n'
                '  "description": string,\n'
                '  "instructions": string,\n'
                '  "cuisine": string,\n'
                '  "prep_time": integer (minutes),\n'
                '  "cook_time": integer (minutes),\n'
                '  "total_time": integer (minutes),\n'
                '  "ingredients": array of strings (format each as "ingredient: amount")\n'
                "}"
            )

            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()

            llm_response = response.json().get("response", "")
            json_content = self.extract_json_from_response(llm_response)

            recipe_data = json.loads(json_content)
            recipe_data = self.clean_recipe_data(recipe_data)

            if save_recipe:
                saved_recipe = self.save_recipe(recipe_data, recipe)
                return Response(
                    {
                        "mmessage": "Recipe updated successfully",
                        "recipe_id": saved_recipe.id,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(recipe_data, status=status.HTTP_200_OK)

        except json.JSONDecodeError as e:
            print("Raw Response:", llm_response)
            print("Extracted JSON:", json_content)
            return Response(
                {"error": f"Failed to parse recipe: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
