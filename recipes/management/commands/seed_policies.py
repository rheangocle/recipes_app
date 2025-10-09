from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
import json, pathlib

from recipes.models import Tag, DietType
from recipes.models.policy import DietTypeRule, DietProtocol, DietProtocolRule

class Command(BaseCommand):
    help = "Seed tags, diet types, and protocols from data/policies.json"
    
    def add_arguments(self, parser):
        parser.add_argument("--file", default="data/policies.json")
        
    @transaction.atomic
    def handle(self, *args, **opts):
        p = pathlib.Path(opts["file"])
        if not p.exists():
            self.stderr.write(self.style.ERROR(f"Seed file not found: {p}"))
            return
        
        data = json.loads(p.read_text())
        
        tag_map = {}
        for name in data.get("tags", []):
            t, _ = Tag.objects.get_or_create(name=name)
            tag_map[name] = t
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(tag_map)} tags"))
        
        for dt in data.get("diet_types", []):
            diet, _ = DietType.objects.get_or_create(name=dt["name"])
            count = 0
            for r in dt.get("rules", []):
                DietTypeRule.objects.get_or_create(
                    diet_type=diet,
                    tag=tag_map[r["tag"]],
                    defaults={"rule": r["rule"]}
                )
                count +=1
            self.stdout.write(self.style.SUCCESS(f"DietType {diet.name}: {count} rules"))
            
        for pr in data.get("protocols", []):
            prot, _ = DietProtocol.objects.get_or_create(name=pr["name"])
            phase_count = 0
            for ph in pr.get("phases", []):
                for r in ph.get("rules", []):
                    DietProtocolRule.objects.get_or_create(
                    protocol=prot,
                        tag=tag_map[r["tag"]],
                        phase=ph["name"],
                        defaults={
                            "rule": r["rule"],
                            "threshold": r.get("threshold")
                        }
                    )
                    phase_count += 1
                self.stdout.write(self.style.SUCCESS(f"Protocol {prot.name}: {phase_count} phase rules"))

            self.stdout.write(self.style.SUCCESS("Policy seed complete."))