from django.contrib import admin
from .models import Server, ServerStat, WarningStat

admin.site.register([Server, ServerStat, WarningStat])

