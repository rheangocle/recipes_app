from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import re
from .models import Recipe


class GenerateRecipeView(APIView):
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

    def post(self, request):
        try:
            ingredients = request.data.get("ingredients", [])
            preferences = request.data.get("preferences", "")
            dietary_restrictions = request.data.get("dietary_restrictions", "")
            cuisine = request.data.get("cuisine", "")
            save_recipe = request.data.get("save", False)

            # Build prompt
            prompt = (
                f"Generate a recipe using these ingredients: {', '.join(ingredients)}. "
                f"Preferences: {preferences}. Cuisine: {cuisine}. "
                f"Dietary restrictions: {dietary_restrictions}. "
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
                Recipe.objects.create(**recipe_data)

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
