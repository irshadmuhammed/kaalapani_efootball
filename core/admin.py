from django.contrib import admin
from .models import Tournament, Team, Match, TopScorer

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'goals_scored', 'goals_conceded', 'goal_difference')
    list_filter = ('tournament',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tournament', 'winner', 'round')
    list_filter = ('tournament', 'round')

@admin.register(TopScorer)
class TopScorerAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'team', 'goals')
    list_filter = ('team__tournament', 'team')
