from django.contrib import admin
from .users.models import User, Organisation
# Register your models here.

    
admin.site.register(User)
admin.site.register(Organisation)