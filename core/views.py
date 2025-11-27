from django.shortcuts import render
from .models import Tournament, Team, Match, TopScorer

def get_current_tournament():
    # Helper to get the first tournament or None
    return Tournament.objects.first()

def home(request):
    # Home is now a dashboard
    return render(request, 'core/home.html')

from .utils import calculate_standings

def standings(request):
    tournament = get_current_tournament()
    teams = []
    if tournament:
        # Calculate standings on the fly to ensure accuracy
        calculate_standings(tournament)
        
        # Sort by Points (desc), then Goal Difference (desc), then Goals Scored (desc)
        teams = tournament.teams.all()
        teams = sorted(teams, key=lambda t: (t.points, t.goal_difference, t.goals_scored), reverse=True)
    
    context = {
        'tournament': tournament,
        'teams': teams,
        'page': 'standings'
    }
    return render(request, 'core/standings.html', context)

def match_generator(request):
    tournament = get_current_tournament()
    teams = []
    if tournament:
        teams = list(tournament.teams.values_list('name', flat=True))
    return render(request, 'core/match_generator.html', {'teams': teams})

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

# --- Custom Admin Views ---
from django.shortcuts import redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .forms import MatchForm
from .utils import calculate_standings, update_top_scorers

@staff_member_required
def match_list(request):
    matches = Match.objects.all().select_related('team_a', 'team_b').order_by('-id')
    return render(request, 'core/admin/match_list.html', {'matches': matches})

@staff_member_required
def match_add(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save()
            # Auto-recalculate
            calculate_standings(match.tournament)
            update_top_scorers(match.tournament)
            return redirect('match_list')
    else:
        form = MatchForm()
    return render(request, 'core/admin/match_form.html', {'form': form, 'title': 'Add Match'})

@staff_member_required
def match_edit(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save()
            calculate_standings(match.tournament)
            update_top_scorers(match.tournament)
            return redirect('match_list')
    else:
        form = MatchForm(instance=match)
    return render(request, 'core/admin/match_form.html', {'form': form, 'title': 'Edit Match'})

@staff_member_required
def match_delete(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == 'POST':
        tournament = match.tournament
        match.delete()
        calculate_standings(tournament)
        update_top_scorers(tournament)
        return redirect('match_list')
    return render(request, 'core/admin/match_confirm_delete.html', {'match': match})
