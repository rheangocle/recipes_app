from django.db import migrations

def seed_diet_data(apps, schema_editor):
    DietType = apps.get_model('recipes', 'DietType')
    DietaryRestriction = apps.get_model('recipes', 'DietaryRestriction')
    
    # Create common diet types
    diet_types = [
        {'name': 'Omnivore', 'description': 'Eats both plant and animal foods'},
        {'name': 'Vegetarian', 'description': 'No meat, but may consume dairy and eggs'},
        {'name': 'Vegan', 'description': 'No animal products or by-products'},
        {'name': 'Pescatarian', 'description': 'Vegetarian diet that includes fish and seafood'},
        {'name': 'Low FODMAP', 'description': 'Low in fermentable oligosaccharides, disaccharides, monosaccharides, and polyols'},
        {'name': 'Keto', 'description': 'Very low-carb, high-fat diet'},
        {'name': 'Paleo', 'description': 'Based on foods presumed to be available to Paleolithic humans'},
        {'name': 'Mediterranean', 'description': 'Based on the traditional foods of countries bordering the Mediterranean Sea'},
        {'name': 'Gluten-Free', 'description': 'Excludes gluten-containing grains'},
        {'name': 'Dairy-Free', 'description': 'Excludes all dairy products'},
        {'name': 'Nut-Free', 'description': 'Excludes all tree nuts and peanuts'},
        {'name': 'Halal', 'description': 'Follows Islamic dietary laws'},
        {'name': 'Kosher', 'description': 'Follows Jewish dietary laws'},
    ]
    
    for diet_type_data in diet_types:
        DietType.objects.get_or_create(
            name=diet_type_data['name'],
            defaults={'description': diet_type_data['description']}
        )
    
    # Create common dietary restrictions
    dietary_restrictions = [
        {'name': 'Gluten Intolerance', 'description': 'Cannot digest gluten protein'},
        {'name': 'Lactose Intolerance', 'description': 'Cannot digest lactose sugar in dairy'},
        {'name': 'Nut Allergy', 'description': 'Allergic to tree nuts and/or peanuts'},
        {'name': 'Shellfish Allergy', 'description': 'Allergic to shellfish and crustaceans'},
        {'name': 'Egg Allergy', 'description': 'Allergic to eggs'},
        {'name': 'Soy Allergy', 'description': 'Allergic to soy products'},
        {'name': 'Wheat Allergy', 'description': 'Allergic to wheat specifically'},
        {'name': 'Fish Allergy', 'description': 'Allergic to fish'},
        {'name': 'Milk Allergy', 'description': 'Allergic to cow\'s milk protein'},
        {'name': 'Sulfite Sensitivity', 'description': 'Sensitive to sulfites in foods'},
        {'name': 'Histamine Intolerance', 'description': 'Cannot process histamine in foods'},
        {'name': 'FODMAP Sensitivity', 'description': 'Sensitive to certain fermentable carbohydrates'},
        {'name': 'Nightshade Sensitivity', 'description': 'Sensitive to nightshade family vegetables'},
        {'name': 'Oxalate Sensitivity', 'description': 'Sensitive to high-oxalate foods'},
    ]
    
    for restriction_data in dietary_restrictions:
        DietaryRestriction.objects.get_or_create(
            name=restriction_data['name'],
            defaults={'description': restriction_data['description']}
        )

def reverse_seed_diet_data(apps, schema_editor):
    DietType = apps.get_model('recipes', 'DietType')
    DietaryRestriction = apps.get_model('recipes', 'DietaryRestriction')
    
    # Remove seeded data
    DietType.objects.filter(
        name__in=['Omnivore', 'Vegetarian', 'Vegan', 'Pescatarian', 'Low FODMAP', 
                  'Keto', 'Paleo', 'Mediterranean', 'Gluten-Free', 'Dairy-Free', 
                  'Nut-Free', 'Halal', 'Kosher']
    ).delete()
    
    DietaryRestriction.objects.filter(
        name__in=['Gluten Intolerance', 'Lactose Intolerance', 'Nut Allergy', 
                  'Shellfish Allergy', 'Egg Allergy', 'Soy Allergy', 'Wheat Allergy',
                  'Fish Allergy', 'Milk Allergy', 'Sulfite Sensitivity', 
                  'Histamine Intolerance', 'FODMAP Sensitivity', 'Nightshade Sensitivity',
                  'Oxalate Sensitivity']
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0003_alter_recipe_fodmap_friendly'),
    ]

    operations = [
        migrations.RunPython(seed_diet_data, reverse_seed_diet_data),
    ]
