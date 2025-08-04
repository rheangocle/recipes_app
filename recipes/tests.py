from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from recipes.models import (
    Recipe, 
    Ingredient, 
    Category, 
    Unit, 
    RecipeIngredient,
    FodmapCategory,
    UserProfile,
    DietType,
    DietaryRestriction,
    FoodPreference
)
import json
from unittest.mock import patch


class FODMAPRecipeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = Category.objects.create(name='Vegetables')
        self.unit = Unit.objects.create(name='cup', unit_type='volume')
        self.fodmap_category = FodmapCategory.objects.create(
            name='Low FODMAP',
            description='Safe for IBS'
        )
        
        self.ingredient1 = Ingredient.objects.create(
            name='carrot',
            category=self.category,
            default_unit=self.unit,
            fodmap_category=self.fodmap_category
        )
        
        self.ingredient2 = Ingredient.objects.create(
            name='chicken breast',
            category=self.category,
            default_unit=self.unit,
            fodmap_category=self.fodmap_category
        )
        
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='A test recipe',
            instructions='Cook the ingredients',
            cuisine='Test Cuisine',
            prep_time=10,
            cook_time=20,
            total_time=30,
            servings=4,
            fodmap_friendly=True,
            fodmap_notes='This recipe is FODMAP friendly'
        )
        
        # Add ingredients to recipe
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient1,
            quantity='2',
            unit=self.unit
        )

    def test_url_routing(self):
        """Test that the URLs are properly routed"""
        # Test GET request to see if the endpoint exists
        response = self.client.get('/api/recipes/generate/')
        # Should return 405 Method Not Allowed for GET, but endpoint should exist
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        response = self.client.get('/api/recipes/update/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_recipe_creation_with_fodmap_fields(self):
        """Test that recipes can be created with FODMAP fields"""
        recipe = Recipe.objects.create(
            title='FODMAP Recipe',
            description='A FODMAP friendly recipe',
            instructions='Cook safely',
            fodmap_friendly=True,
            fodmap_notes='Safe for IBS'
        )
        
        self.assertTrue(recipe.fodmap_friendly)
        self.assertEqual(recipe.fodmap_notes, 'Safe for IBS')
        self.assertTrue(recipe.fodmap_friendly)  # Should default to True

    @patch('requests.post')
    def test_generate_recipe_endpoint(self, mock_post):
        """Test the recipe generation endpoint"""
        # Mock the LLM response
        mock_response = {
            'response': '''
            ```json
            {
                "title": "Carrot Chicken Stir Fry",
                "description": "A delicious low FODMAP stir fry",
                "instructions": "Cook chicken and carrots together",
                "cuisine": "Asian",
                "prep_time": 10,
                "cook_time": 15,
                "total_time": 25,
                "servings": 4,
                "ingredients": [
                    {
                        "name": "carrot",
                        "quantity": "2",
                        "unit": "cups"
                    },
                    {
                        "name": "chicken breast",
                        "quantity": "1",
                        "unit": "pound"
                    }
                ],
                "fodmap_friendly": true,
                "fodmap_notes": "All ingredients are low FODMAP"
            }
            ```
            '''
        }
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status.return_value = None
        
        response = self.client.post('/api/recipes/generate/', {
            'ingredients': ['carrot', 'chicken breast'],
            'preferences': 'Low FODMAP diet',
            'dietary_restrictions': 'Low FODMAP',
            'cuisine': 'Asian',
            'save': False
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['title'], 'Carrot Chicken Stir Fry')
        self.assertTrue(data['fodmap_friendly'])

    @patch('requests.post')
    def test_update_recipe_endpoint(self, mock_post):
        """Test the recipe update endpoint"""
        # Mock the LLM response
        mock_response = {
            'response': '''
            ```json
            {
                "title": "Updated FODMAP Recipe",
                "description": "Updated description",
                "instructions": "Updated instructions",
                "cuisine": "Mediterranean",
                "prep_time": 15,
                "cook_time": 25,
                "total_time": 40,
                "servings": 6,
                "ingredients": [
                    {
                        "name": "carrot",
                        "quantity": "3",
                        "unit": "cups"
                    }
                ],
                "fodmap_friendly": true,
                "fodmap_notes": "Updated FODMAP notes"
            }
            ```
            '''
        }
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status.return_value = None
        
        response = self.client.post('/api/recipes/update/', {
            'recipe_id': self.recipe.id,
            'title': 'Updated FODMAP Recipe',
            'description': 'Updated description',
            'instructions': 'Updated instructions',
            'cuisine': 'Mediterranean',
            'prep_time': 15,
            'cook_time': 25,
            'total_time': 40,
            'servings': 6,
            'ingredients': ['carrot'],
            'preferences': 'Low FODMAP diet',
            'dietary_restrictions': 'Low FODMAP',
            'cuisine': 'Mediterranean',
            'save': False
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['title'], 'Updated FODMAP Recipe')
        self.assertTrue(data['fodmap_friendly'])

    def test_user_preferences_integration(self):
        """Test that user preferences are properly integrated"""
        # Get the existing user profile (created by signal)
        profile = UserProfile.objects.get(user=self.user)
        
        # Create diet type and restriction
        diet_type = DietType.objects.create(name='Low FODMAP')
        restriction = DietaryRestriction.objects.create(name='Gluten Free')
        
        # Update the existing profile
        profile.diet_type = diet_type
        profile.save()
        profile.dietary_restrictions.add(restriction)
        
        # Create food preferences
        FoodPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient1,
            preference='like'
        )
        
        FoodPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient2,
            preference='allergic'
        )
        
        # Test that preferences are accessible
        self.assertEqual(profile.diet_type.name, 'Low FODMAP')
        self.assertEqual(profile.dietary_restrictions.count(), 1)

    def test_recipe_ingredient_relationship(self):
        """Test recipe-ingredient relationships"""
        recipe_ingredient = RecipeIngredient.objects.get(
            recipe=self.recipe,
            ingredient=self.ingredient1
        )
        
        self.assertEqual(recipe_ingredient.quantity, '2')
        self.assertEqual(recipe_ingredient.unit, self.unit)
        self.assertEqual(str(recipe_ingredient), '2 cup carrot in Test Recipe')

    def test_fodmap_category_functionality(self):
        """Test FODMAP category functionality"""
        high_fodmap = FodmapCategory.objects.create(
            name='High FODMAP',
            description='Avoid for IBS'
        )
        
        self.assertEqual(str(high_fodmap), 'High FODMAP')
        self.assertEqual(high_fodmap.description, 'Avoid for IBS')

    def test_recipe_serialization(self):
        """Test that recipes serialize correctly with FODMAP fields"""
        from recipes.serializers import RecipeSerializer
        
        serializer = RecipeSerializer(self.recipe)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test Recipe')
        self.assertTrue(data['fodmap_friendly'])
        self.assertEqual(data['fodmap_notes'], 'This recipe is FODMAP friendly')
        # Check if ingredients_detail exists and has the expected length
        self.assertIn('ingredients_detail', data)
        self.assertEqual(len(data['ingredients_detail']), 1)

    def test_invalid_recipe_id(self):
        """Test handling of invalid recipe ID in update endpoint"""
        response = self.client.post('/api/recipes/update/', {
            'recipe_id': 99999,  # Non-existent ID
            'ingredients': ['carrot']
        })
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_recipe_id(self):
        """Test handling of missing recipe ID in update endpoint"""
        response = self.client.post('/api/recipes/update/', {
            'ingredients': ['carrot']
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('recipe id is required', response.json()['error'])

    def test_ingredient_validation(self):
        """Test ingredient validation in generate endpoint"""
        response = self.client.post('/api/recipes/generate/', {
            'ingredients': [],  # Empty ingredients list
            'save': False
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fodmap_friendly_default(self):
        """Test that new recipes default to FODMAP friendly"""
        recipe = Recipe.objects.create(
            title='New Recipe',
            description='A new recipe',
            instructions='Cook it'
        )
        
        self.assertTrue(recipe.fodmap_friendly)  # Should default to True
