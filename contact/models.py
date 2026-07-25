from enum import unique

from django.db import models

# Create your models here.

class ContactStatusChoices(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    city_of_residence = models.CharField(max_length=100)
    status = models.ForeignKey(ContactStatusChoices, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"