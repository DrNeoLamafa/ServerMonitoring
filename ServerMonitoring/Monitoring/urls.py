from django.urls import path
from .views import CheckState

urlpatterns = [
    path('', CheckState)
]
