from django.db import models
from django.contrib.auth.models import User
class Student(models.Model):
    name = models.CharField(max_length=100)
    roll = models.IntegerField()
    email = models.EmailField()
    department = models.CharField(max_length=100)
    age = models.IntegerField()
    
    created_by = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='students'
)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
     return self.name