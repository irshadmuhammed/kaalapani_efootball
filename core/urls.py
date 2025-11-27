from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('points-table/', views.standings, name='standings'),
    path('bracket/', views.bracket, name='bracket'),
    path('top-scorers/', views.top_scorers, name='top_scorers'),
    path('upcoming/', views.upcoming_matches, name='upcoming'),
    path('match-generator/', views.match_generator, name='match_generator'),
]
