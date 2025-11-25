from django.shortcuts import render
from .models import Tournament, Team, Match, TopScorer

def get_current_tournament():
    # Helper to get the first tournament or None
    return Tournament.objects.first()

def home(request):
    tournament = get_current_tournament()
    teams = []
    if tournament:
        teams = tournament.teams.all().order_by('-goals_scored') # Simple sorting for now, can improve
        # Calculate points/GD if we had match results logic fully fleshed out, 
        # but for now we rely on the model fields which we assume are updated.
        # Let's sort by points (if we had them) -> GD -> Goals Scored.
        # Since we only have goals_scored/conceded, let's sort by (goals_scored - goals_conceded) desc.
        teams = sorted(teams, key=lambda t: t.goal_difference, reverse=True)
    
    context = {
        'tournament': tournament,
        'teams': teams,
        'page': 'standings'
    }
    return render(request, 'core/home.html', context)

def bracket(request):
    tournament = get_current_tournament()
    matches = []
    if tournament:
        matches = tournament.matches.all().select_related('team_a', 'team_b', 'winner')
    
    # Organize matches by round for easier template rendering
    rounds = {
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
