from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('points-table/', views.standings, name='standings'),
    path('bracket/', views.bracket, name='bracket'),
    path('top-scorers/', views.top_scorers, name='top_scorers'),
    path('upcoming/', views.upcoming_matches, name='upcoming'),
    
    # Custom Admin
    path('custom-admin/matches/', views.match_list, name='match_list'),
    path('custom-admin/matches/add/', views.match_add, name='match_add'),
    path('custom-admin/matches/<int:pk>/edit/', views.match_edit, name='match_edit'),
    path('custom-admin/matches/<int:pk>/delete/', views.match_delete, name='match_delete'),
    path('match-generator/', views.match_generator, name='match_generator'),
]
