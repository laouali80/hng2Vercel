from django.urls import path
from . import views


urlpatterns = [
    path('', views.test, name='test'),
    path('auth/register', views.register, name='register'),
    path('auth/login', views.login, name='login'),
    path('api/users/<str:id>', views.get_user_record, name='get_user'),
    path('api/organisations', views.get_or_create_organisations, name='get_or_create_organisations'),
    path('api/organisations/<str:orgId>', views.get_organisation, name='get_organisation'),
    
    path('api/organisations/<str:orgId>/users', views.add_user, name='add_user'),
]
