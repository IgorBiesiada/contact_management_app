from enum import unique
from tokenize import blank_re
from django.db import models
from users.models import CustomUser
# Create your models here.

class ContactStatusChoices(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    city_of_residence = models.CharField(max_length=100)
    status = models.ForeignKey(ContactStatusChoices, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email', 'phone_number'], name='unique_user_phone'),
            models.UniqueConstraint(fields=['user', 'email'], name='unique_user_email'),
        ]


    def __str__(self):
        return f"{self.first_name} {self.last_name}"