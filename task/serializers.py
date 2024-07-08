# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .users.models import Organisation
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    # userId = serializers.UUIDField(source='userId')

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
            return Response({
                    "errors": [
                        {
                        "field": "FirstName",
                        "message": "name must not be null."
                        },
                    ]
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return value
    

    def validate_lastName(self, value):
        if len(value) < 1:
            return Response({
                "errors": [
                    {
                    "field": "LastName",
                    "message": "must not be null."
                    },
                ]
            }, status= status.HTTP_422_UNPROCESSABLE_ENTITY)
        return value
    

    def validate_email(self, value):
        if len(value) < 1:
            return Response({
                "errors": [
                    {
                    "field": "Email",
                    "message": "must be unique and not null."
                    },
                ]
            }, status= status.HTTP_422_UNPROCESSABLE_ENTITY)
        return value

    def create(self, validated_data):
        user = User.objects.create(
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
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
            return Response({
                "errors": [
                    {
                    "field": "Organisation Name",
                    "message": "Required and cannot be null"
                    },
                ]
            }, status= status.HTTP_422_UNPROCESSABLE_ENTITY)
        return value

    def create(self, validated_data):
        try:
            name = f"{validated_data['name'].title()}'s Organisation"
            organisation = Organisation.objects.create(
                name=name,
                description=validated_data['description']
            )
            organisation.save()
        except IntegrityError as e:
            raise serializers.ValidationError(str(e))
        
        return organisation
    
    
