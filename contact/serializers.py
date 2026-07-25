from rest_framework import serializers
from .models import Contact, ContactStatusChoices

class ContactSerializer(serializers.ModelSerializer):
    #uses SlugRelatedField to return the readable status name
    status = serializers.SlugRelatedField(queryset=ContactStatusChoices.objects.all(), slug_field='name')

    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'city_of_residence', 'status', 'date']

class ContactDetailSerializer(serializers.ModelSerializer):
    status = serializers.SlugRelatedField(queryset=ContactStatusChoices.objects.all(), slug_field='name')

    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'city_of_residence', 'status']