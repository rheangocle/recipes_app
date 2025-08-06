# FODMAP Recipe App Backend

A Django REST API backend for a FODMAP-friendly recipe application designed to help users with IBS and digestive sensitivities find, create, and manage low-FODMAP recipes.

## 🍽️ Features

### Core Functionality

- **AI-Powered Recipe Generation**: Generate FODMAP-friendly recipes using LLM integration
- **Recipe Updates**: Refine existing recipes to be FODMAP-compliant
- **User Preferences**: Track dietary restrictions, allergies, and food preferences
- **FODMAP Categorization**: Organize ingredients by FODMAP levels
- **Recipe Management**: Full CRUD operations for recipes, ingredients, and user data

### FODMAP-Specific Features

- **FODMAP-Friendly Recipe Filtering**: Automatically identify and flag FODMAP-safe recipes
- **Ingredient Substitution**: Suggest FODMAP-friendly alternatives
- **Portion Control**: Include specific serving sizes for FODMAP tolerance
- **FODMAP Notes**: Detailed notes about FODMAP considerations for each recipe

### User Management

- **Authentication**: JWT-based authentication with social login (Google)
- **User Profiles**: Personalized dietary preferences and restrictions
- **Food Preferences**: Track liked, disliked, and allergic ingredients
- **Recipe Preferences**: Save favorite recipes and ratings

## 🏗️ Project Structure

```
recipe_app/
├── recipe_backend/          # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI application
├── recipes/               # Main Django app
│   ├── models/           # Database models
│   │   ├── base.py       # Base model with common fields
│   │   ├── recipe.py     # Recipe, Ingredient, and related models
│   │   └── user.py       # User profile and preference models
│   ├── views/            # API views
│   │   ├── generate_recipe_view.py    # AI recipe generation
│   │   ├── update_recipe_view.py      # Recipe refinement
│   │   ├── viewsets.py               # REST API viewsets
│   │   ├── auth_views.py             # Authentication views
│   │   ├── shopping_list_views.py    # Shopping list functionality
│   │   └── stats_views.py            # User statistics
│   ├── serializers.py    # DRF serializers
│   ├── urls.py          # URL routing
│   ├── admin.py         # Django admin configuration
│   ├── cache_utils.py   # Caching utilities
│   ├── permissions.py   # Custom permissions
│   ├── signals.py       # Django signals
│   └── tests.py         # Test suite
├── requirements.txt     # Python dependencies
├── manage.py           # Django management script
└── README.md          # This file
```

## 🔧 Configuration

### LLM Integration

The app integrates with Ollama for AI recipe generation:

- **Generate Recipe**: Uses `deepseek-coder:1.3b`
- **Update Recipe**: Uses `llama3.2:1b`
- **Endpoint**: `http://localhost:11434/api/generate`

## 📚 API Documentation

### Authentication Endpoints

```
POST /auth/login/                    # User login
POST /auth/logout/                   # User logout
POST /auth/registration/             # User registration
POST /auth/google/login/callback/    # Google OAuth callback
GET  /user/details/                  # Get user details
GET  /user/statistics/               # Get user statistics
```

### Recipe Endpoints

```
GET    /api/recipes/                 # List all recipes
POST   /api/recipes/                 # Create new recipe
GET    /api/recipes/{id}/            # Get recipe details
PUT    /api/recipes/{id}/            # Update recipe
DELETE /api/recipes/{id}/            # Delete recipe
POST   /api/recipes/generate/        # Generate AI recipe
POST   /api/recipes/update/          # Update recipe with AI
```

### Recipe Generation

**Endpoint**: `POST /api/recipes/generate/`

**Request Body**:

```json
{
  "ingredients": ["carrot", "chicken breast"],
  "preferences": "Low FODMAP diet",
  "dietary_restrictions": "Low FODMAP",
  "cuisine": "Asian",
  "save": false
}
```

**Response**:

```json
{
  "title": "Carrot Chicken Stir Fry",
  "description": "A delicious low FODMAP stir fry",
  "instructions": "Cook chicken and carrots together...",
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
    }
  ],
  "fodmap_friendly": true,
  "fodmap_notes": "All ingredients are low FODMAP"
}
```

### Recipe Update

**Endpoint**: `POST /api/recipes/update/`

**Request Body**:

```json
{
  "recipe_id": 1,
  "ingredients": ["carrot"],
  "preferences": "Low FODMAP diet",
  "dietary_restrictions": "Low FODMAP",
  "cuisine": "Mediterranean",
  "save": true
}
```

### Other Endpoints

```
GET    /api/ingredients/             # List ingredients
GET    /api/categories/              # List categories
GET    /api/fodmap-categories/       # List FODMAP categories
GET    /api/units/                   # List measurement units
GET    /api/tags/                    # List recipe tags
GET    /api/user-profile/            # User profile management
GET    /api/food-preferences/        # Food preferences
GET    /api/inventory/               # User inventory
GET    /api/feedback/                # Recipe feedback
GET    /shopping-list/               # Shopping list
```

## 🗄️ Database Models

### Core Models

- **Recipe**: Main recipe entity with FODMAP-specific fields
- **Ingredient**: Ingredients with FODMAP categorization
- **RecipeIngredient**: Many-to-many relationship with quantities
- **UserProfile**: Extended user information and preferences
- **FoodPreference**: User food likes/dislikes/allergies
- **FodmapCategory**: FODMAP classification system

### Key Fields

- `fodmap_friendly`: Boolean flag for FODMAP compliance
- `fodmap_notes`: Detailed FODMAP considerations
- `fodmap_category`: Ingredient FODMAP classification
- `dietary_restrictions`: User dietary limitations
- `allergic_ingredients`: User allergy tracking

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: API rate limiting (10 requests/hour for recipe generation)
- **CORS Support**: Cross-origin resource sharing configuration
- **Input Validation**: Comprehensive input validation and sanitization

## 📱 Mobile Frontend

The mobile frontend for this application is located at: `https://github.com/rheangocle/recipe-app-react-native`

---

**Note**: This application is designed specifically for users with IBS and digestive sensitivities. Always consult with healthcare professionals regarding dietary changes.
