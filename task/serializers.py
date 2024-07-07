# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .users.models import Organisation
from django.http import JsonResponse

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    userId = serializers.UUIDField(source='userId')

    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'phone']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'email', 'password', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_firstName(self, value):
        if len(value) < 1:
            return JsonResponse({
                    "errors": [
                        {
                        "field": "First Name",
                        "message": "The first name must contain at least 3 letters (e.g: Tim)."
                        },
                    ]
                }, status= 422)
        return value
    

    def validate_lastName(self, value):
        if len(value) < 1:
            return JsonResponse({
                "errors": [
                    {
                    "field": "Last Name",
                    "message": "The last name must contain at least 3 letters (e.g: Jim)."
                    },
                ]
            }, status= 422)
    

    def validate_email(self, value):
        if len(value) < 1 or '@gmail.com' not in value:
            return JsonResponse({
                "errors": [
                    {
                    "field": "Email",
                    "message": "Email must be unique and not null."
                    },
                ]
            }, status= 422)

    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            phone=validated_data['phone']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class OrganisationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']



class CreateOrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['name', 'description']

    def validate_name(self, value):
        if len(value) < 1:
            return JsonResponse({
                "errors": [
                    {
                    "field": "Organisation Name",
                    "message": "The name cannot be null."
                    },
                ]
            }, status= 422)

    def create(self, validated_data):
        name = f"{validated_data['name'].title()}'s Organisation"
        organisation = Organisation.objects.create(
            name=name,
            description=validated_data['description']
        )
        organisation.save()
        return organisation
    
    