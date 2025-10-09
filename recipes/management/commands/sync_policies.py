from django.core.management.base import BaseCommand
from django.db import transaction
import requests
from recipes.models import Tag, DietType
from recipes.models.policy import DietTypeRule, DietProtocol, DietProtocolRule

POLICY_URL = "https://policy.yourdomain.com/api/v1/policies"  # replace

class Command(BaseCommand):
    help = "Sync tags/diet types/protocols from remote policy API"
    
    @transaction.atomic
    def handle(self, *args, **opts):
        resp = requests.get(POLICY_URL, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        
        tag_map = {}
        for name in data.get("tags", []):
            t, _ = Tag.objects.get_or_create(name=name)
            tag_map[name] = t
            
        for dt in data.get("diet_types", []):
            diet, _ = DietType.objects.get_or_create(name=dt["name"])
            for r in dt.get("rules", []):
                DietTypeRule.objects.update_or_create(
                    diet_type=diet,
                    tag=tag_map[r["tag"]],
                    defaults={"rule": r["rule"]}
                )
                
        for pr in data.get("protocols", []):
            prot, _ = DietProtocol.objects.get_or_create(name=pr["name"])
            for ph in pr.get("phases", []):
                for r in ph.get("rules", []):
                    DietProtocolRule.objects.update_or_create(
                        protocol=prot,
                        tag=tag_map[r["tag"]],
                        phase=ph["name"],
                        defaults={"rule": r["rule"], "threshold": r.get("threshold")}
                    )
                    
        self.stdout.write(self.style.SUCCESS("Policy sync complete."))
                    