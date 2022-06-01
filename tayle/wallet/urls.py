from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.index, name='index'),
    path('transfer', views.transfer, name='transfer'),
]