from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('bracket/', views.bracket, name='bracket'),
    path('top-scorers/', views.top_scorers, name='top_scorers'),
]
