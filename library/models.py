from django.db import models
from members.models import Member

class Library(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    @property
    def members(self):
        return Member.objects.all()