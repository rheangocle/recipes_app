from dataclasses import dataclass, field
from re import L
from typing import Dict, Set, Optional
from django.db.models import Q
from recipes.models import Tag, Ingredient, UserProfile
from recipes.models.policy import DietTypeRule, RestrictionRule, DietProtocolRule

@dataclass
class CompiledPolicy:
    forbidden_tag_ids: Set[int] = field(default_factory=set)
    forbidden_ingredient_ids: Set[int] = field(default_factory=set)
    limits_by_tag_id: Dict[int, float] = field(default_factory=dict)
    protocol_name: Optional[str] = None
    protocol_phase: Optional[str] = None
    diet_type_names: Set[str] = field(default_factory=set)
    restriction_names: Set[str] = field(default_factory=set)
    
def compile_policy_for_user(user) -> CompiledPolicy:
    p = CompiledPolicy()
    profile = UserProfile.objects.select_related('user').prefetch_related('diet_types', 'dietary_restrictions').get(user=user)
    
    p.diet_type_names = set(profile.diet_types.values_list('name', flat=True))
    p.restriction_names = set(profile.dietary_restrictions.values_list('name', flat=True))
    
    dt_rules = DietTypeRule.objects.filter(diet_type__in=profile.diet_types.all())
    for r in dt_rules:
        if r.rule == DietTypeRule.Rule.AVOID:
            p.forbidden_tag_ids.add(r.tag_id)
        elif r.rule == DietTypeRule.Rule.LIMIT and r.tag_id:
            p.limits_by_tag_id.setdefault(r.tag_id, float('inf'))
            
    rs_rules = RestrictionRule.objects.filter(restriction__in=profile.dietary_restrictions.all())
    for r in rs_rules:
        if r.ingredient_id: 
            if r.rule == RestrictionRule.Rule.AVOID:
                p.forbidden_ingredient_ids.add(r.ingredient_id)
            elif r.rule == RestrictionRule.Rule.LIMIT and r.threshold:
                pass
        elif r.tag_id:
            if r.rule == RestrictionRule.Rule.AVOID:
                p.forbidden_tag_ids.add(r.tag_id)
            elif r.rule == RestrictionRule.Rule.LIMIT and r.threshold is not None:
                p.limits_by_tag_id[r.tag_id] = r.threshold
                
    user_protocols = getattr(user, 'protocols', None)
    if user_protocols and user_protocols.exists():
        up = user_protocols.get(is_primary=True)
        p.protocol_name, p.protocol_phase = up.protocol.name, up.phase
        pr_rules = DietProtocolRule.objects.filter(protocol=up.protocol, phase=up.phase)
        for r in pr_rules:
            if r.rule == DietProtocolRule.Rule.AVOID:
                p.forbidden_tag_ids.add(r.tag_id)
            elif r.rule == DietProtocolRule.Rule.LIMIT and r.threshold is not None:
                p.limits_by_tag_id[r.tag_id] = r.threshold
    return p

            
    