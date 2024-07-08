from django.shortcuts import redirect
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .users.models import User, Organisation
from .serializers import UserSerializer, RegisterSerializer, CreateOrganisationSerializer, OrganisationSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([AllowAny])
def welcome(request):
    return redirect('register')

@api_view(['GET','POST'])
@permission_classes([AllowAny])
def register(request):
    """Registers a users and creates a default organisation."""
    
    if request.method == "POST":
        
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            user_data = UserSerializer(user).data
 

            # Create an organization using the validated user data
            orga_creation_data = {
                "name": user_data["firstName"],
                "description": ''
            }
            orga_serializer = CreateOrganisationSerializer(data=orga_creation_data)
            
            if orga_serializer.is_valid():
                save_org = orga_serializer.save()
                user = User.objects.get(pk=user_data["userId"])
                user.organisations.add(save_org)

                return Response({
                    "status": "success",
                    "message": "Registration successful",
                    "data": {
                        "accessToken": access_token,
                        "user": user_data
                        }
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "status": "Bad request",
                    "message": "Registration unsuccessful",
                    "statusCode": 400,
                    "errors": orga_serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        
        resp = {
                "errors": [
                    {
                        "field": list(serializer.errors.keys())[0],
                        "message": serializer.errors[f"{list(serializer.errors.keys())[0]}"][0]
                    }
                ]
            }
        return Response(resp, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
    else:
        return Response({
                    "status": "Method not allowed",
                    "message": "This request method is not allow.",
                    "statusCode": 400
                }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','POST'])
@permission_classes([AllowAny])
def login(request):
    """Logs in a user and returns a JWT access token."""

    if request.method == "POST":
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            user_data = UserSerializer(user).data

            return Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": access_token,
                    "user": user_data
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            }, status=status.HTTP_401_UNAUTHORIZED)

    else:
        return Response({
                    "status": "Method not allowed",
                    "message": "This request method is not allow.",
                    "statusCode": 405
                }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def get_user_record(request, id:str = None):
    """Get a user record"""
    
    if request.method == 'GET':
        user = request.user

        try:
            target_user = User.objects.get(pk=id)
        except UnboundLocalError or ValueError:
            return Response("Error 404!! Not found.", status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response("Error 404!! Not found.", status=status.HTTP_404_NOT_FOUND)
        
         # Check if the user is requesting their own record or a record in their organizations
        if target_user == user or user.organisations.filter(pk__in=target_user.organisations.values_list('pk', flat=True)).exists():
            serializer = UserSerializer(target_user, many=False)
            response_data = {
                "status": "success",
                "message": "User record found",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "message": "You do not have permission to view this user."}, status=status.HTTP_403_FORBIDDEN)
        
    else:
        return Response({
            "status": "Method not allowed",
            "message": "This request method is not allow.",
            "statusCode": 405
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def get_or_create_organisations(request):
    """get all user belongings organisations or create a new organisation."""

    if request.method == 'GET':
        organisations = request.user.organisations.all()

        # organisations = 
        serializer = OrganisationSerializer(organisations, many=True)
        response_data = {
                "status": "success",
                "message": "User organisations",
                "data": {
                "organisations": serializer.data
                }
            }
        
        return Response(response_data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        
        new_org_data = {
            "name": request.data.get('name'),
            "description": request.data.get('description')
        }
        new_org_serializer = CreateOrganisationSerializer(data=new_org_data)

        if new_org_serializer.is_valid():
            new_org = new_org_serializer.save()  

            request.user.organisations.add(new_org)

            response_data = {
                "status": "success",
                "message": "Organisation created successfully",
                "data": OrganisationSerializer(new_org).data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
def get_organisation(request, orgId:str = None):
    """Get an organisation with a giving orgId"""

    if request.method == 'GET':
        if orgId:
            try:
                organisation = Organisation.objects.get(pk=orgId)
            except UnboundLocalError or ValueError:
                return Response("Error 404!! Not found.", status=status.HTTP_400_BAD_REQUEST)
            except Organisation.DoesNotExist:
                return Response("Error 404!! Not found.", status=status.HTTP_404_NOT_FOUND)
            
            serializer = OrganisationSerializer(organisation, many=False)

            return Response({
                    "status": "success",
                    "message": "Organisation Found",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
        else:

            organisations = Organisation.objects.all()
            serializer = UserSerializer(organisations, many=True)
            return Response({
                    "status": "success",
                    "message": "<message>",
                    "data": {
                    "organisations": serializer.data
                    }
                }, status=status.HTTP_200_OK)
            
    elif request.method == 'POST':
        serializer = CreateOrganisationSerializer(data=request.data)
        
        if serializer.is_valid():
            organisation = serializer.save()
            organisation_data = OrganisationSerializer(organisation).data

            return Response({
                    "status": "success",
                    "message": "Organisation created successfully",
                    "data": organisation_data
                    }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)

 
    else:
        Response({
            "status": "Method not allowed",
            "message": "This request method is not allow.",
            "statusCode": 405
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user(request, orgId: str = None):
    """Add a user to an organisation."""

    if request.method == 'POST':
        if orgId:
            try:
                organisation = Organisation.objects.get(pk=orgId)
            except UnboundLocalError or ValueError:
                return Response("Error 404!! Not found.", status=status.HTTP_400_BAD_REQUEST)
            except Organisation.DoesNotExist:
                return Response("Error 404!! Not found.", status=status.HTTP_404_NOT_FOUND)
            
            # serializer = OrganisationSerializer(organisation, many=False)

            userId = request.data.get('userId')


            try:
                user = User.objects.get(pk=userId)
            except UnboundLocalError or ValueError:
                return Response("Error 404!! Not found.", status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response("Error 404!! Not found.", status=status.HTTP_404_NOT_FOUND)

            user.organisations.add(organisation)
            
            return Response({
                    "status": "success",
                    "message": "User added to organisation successfully",
                }, status=status.HTTP_200_OK)
        else:

            return Response({
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            "status": "Method not allowed",
            "message": "This request method is not allow.",
            "statusCode": 405
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
