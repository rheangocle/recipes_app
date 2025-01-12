# pylint: disable=no-member

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from decouple import config
import requests


class GenerateRecipeView(APIView):
    
    def post(self, request):
        ingredients = request.data.get('ingredients', [])
        preferences = request.data.get('preferences', '')
        dietary_restrictions = request.data.get('dietary_restrictions', '')
        number_of_recipes = int(request.data.get('num_recipes', 1))
        
        prompt = (
            "You are a recipe-generating assistant. Please follow these instructions carefully:\n\n"
            f"Generate {number_of_recipes} recipe(s) using these ingredients: {', '.join(ingredients)}.\n"
            f"Preferences: {preferences}\n"
            f"Dietary restrictions to avoid: {dietary_restrictions}\n\n"
            "For each recipe, provide:\n"
            "1. Title\n"
            "2. List of ingredients with measurements\n"
            "3. Clear step-by-step instructions\n\n"
            "You can include common pantry items as additional ingredients."
        )
        
        model = 'llama3.2:latest'
        
        try: 
            response = requests.post('http://localhost:11434/api/generate', 
                                     json={
                                         'model': model,
                                         'prompt': prompt,
                                         'stream': False
                                     })
            
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get('response', '')
            print(result)
            return Response({'recipes': generated_text}, status=status.HTTP_200_OK)
        
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            