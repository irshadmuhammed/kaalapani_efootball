from django.contrib import admin
from .models import Tournament, Team, Match, SingleMatch, TopScorer

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'played', 'wins', 'draws', 'losses', 'points')
    list_filter = ('tournament',)
    search_fields = ('name',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team_a', 'team_b', 'round', 'score_a', 'score_b', 'winner')
    list_filter = ('tournament', 'round')
    search_fields = ('team_a__name', 'team_b__name')

@admin.register(SingleMatch)
class SingleMatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'leg', 'match_datetime', 'status')
    list_filter = ('status', 'leg')
    search_fields = ('home_team__name', 'away_team__name')

@admin.register(TopScorer)
class TopScorerAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'team', 'goals')
    list_filter = ('team__tournament',)
    search_fields = ('player_name', 'team__name')
