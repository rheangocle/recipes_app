# pylint: disable=no-member

from django.db import models
from django.utils.timezone import now
import uuid

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        self.is_active = False
        self.deleted_at = now()
        self.save()
        
    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save()
        
    def hard_delete(self):
        super(BaseModel, self).delete()
  