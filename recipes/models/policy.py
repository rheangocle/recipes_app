
# pylint: disable=no-member
 
from django.db import models
from .base import BaseModel
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Q
User = get_user_model()

class DietProtocol(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
class ProtocolPhase(models.TextChoices):
    ELIMINATION = 'elimination', 'Elimination'
    REINTRODUCTION = 'reintroduction', 'Reintroduction'
    PERSONALIZATION = 'personalization', 'Personalization'
    
class DietProtocolRule(BaseModel):
    class Rule(models.TextChoices):
        ALLOW = 'allow', 'Allow'
        AVOID = 'avoid', 'Avoid'
        LIMIT = 'limit', 'Limit'
        
    protocol = models.ForeignKey(DietProtocol, on_delete=models.CASCADE, related_name='rules')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='protocol_rules')
    phase = models.CharField(max_length=20, choices=ProtocolPhase.choices, default=ProtocolPhase.ELIMINATION)
    rule = models.CharField(max_length=8, choices=Rule.choices)
    threshold = models.FloatField(null=True, blank=True, help_text='Per-serving limit for LIMIT rules')

    class Meta: 
        unique_together = ('protocol', 'tag', 'phase')
        
class UserProtocol(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='protocols')
    protocol = models.ForeignKey(DietProtocol, on_delete=models.CASCADE)
    phase = models.CharField(max_length=20, choices=ProtocolPhase.choices, default=ProtocolPhase.ELIMINATION)
    is_primary = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(is_primary=True),
                name='one_primary_protocol_per_user'
            ),
            models.UniqueConstraint(fields=['user', 'protocol'], name='unique_user_protocol')
        ]
        
    def __str__(self) -> str:
        return f"{self.user} - {self.protocol.name} ({self.phase})"
    
class DietTypeRule(BaseModel):
    class Rule(models.TextChoices):
        ALLOW = 'allow', 'Allow'
        AVOID = 'avoid', 'Avoid'
        LIMIT = 'limit', 'Limit'
        
    diet_type = models.ForeignKey('DietType', on_delete=models.CASCADE, related_name='rules')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='diet_type_rules')
    rule = models.CharField(max_length=8, choices=Rule.choices)

    class Meta: 
        unique_together = ('diet_type', 'tag')
        
class RestrictionRule(BaseModel):
    class Rule(models.TextChoices):
        ALLOW = 'allow', 'Allow'
        AVOID = 'avoid', 'Avoid'
        LIMIT = 'limit', 'Limit'
        
    restriction = models.ForeignKey('DietaryRestriction', on_delete=models.CASCADE, related_name='rules')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, null=True, blank=True, related_name='restriction_rules')
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, null=True, blank=True, related_name='restriction_rules')
    rule = models.CharField(max_length=8, choices=Rule.choices)
    threshold = models.FloatField(null=True, blank=True, help_text='Per-serving limit for LIMIT rules')

    class Meta: 
        constraints = [
            models.CheckConstraint(
                check=Q(tag__isnull=False) | Q(ingredient__isnull=False),
                name='restriction_tag_or_ingredient_required'
            )
        ]