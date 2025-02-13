from django.contrib import admin
from .models import Server, ServerStat

admin.site.register(Server)
admin.site.register(ServerStat)
