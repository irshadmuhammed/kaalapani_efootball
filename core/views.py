from django.shortcuts import render
from .models import Tournament, Team, Match, TopScorer

def get_current_tournament():
    # Helper to get the first tournament or None
    return Tournament.objects.first()

def home(request):
    # Home is now a dashboard
    return render(request, 'core/home.html')

def standings(request):
    tournament = get_current_tournament()
    teams = []
    if tournament:
        teams = tournament.teams.all().order_by('-goals_scored')
        teams = sorted(teams, key=lambda t: t.goal_difference, reverse=True)
    
    context = {
        'tournament': tournament,
        'teams': teams,
        'page': 'standings'
    }
    return render(request, 'core/standings.html', context)

def match_generator(request):
    return render(request, 'core/match_generator.html')

def bracket(request):
    tournament = get_current_tournament()
    matches = []
    if tournament:
        matches = tournament.matches.all().select_related('team_a', 'team_b', 'winner')
    
    # Organize matches by round for easier template rendering
    rounds = {
        'R16': [],
        'QF': [],
        'SF': [],
        'F': []
    }
    for m in matches:
        if m.round in rounds:
            rounds[m.round].append(m)
            
    context = {
        'tournament': tournament,
        'rounds': rounds,
        'page': 'bracket'
    }
    return render(request, 'core/bracket.html', context)

def top_scorers(request):
    tournament = get_current_tournament()
    scorers = []
    if tournament:
        scorers = TopScorer.objects.filter(team__tournament=tournament).order_by('-goals')
        
    context = {
        'tournament': tournament,
        'scorers': scorers,
        'page': 'scorers'
    }
    return render(request, 'core/top_scorers.html', context)

def upcoming_matches(request):
    # Fetch matches that are scheduled but not finished (winner is None)
    matches = Match.objects.filter(winner__isnull=True).select_related('team_a', 'team_b').order_by('id')
    return render(request, 'core/upcoming.html', {'matches': matches})
