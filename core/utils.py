from .models import SingleMatch, Team, TopScorer

def calculate_standings(tournament):
    """
    Recalculates standings for all teams in the tournament based on finished matches.
    Updates the Team model fields: played, wins, draws, losses, goals_scored, goals_conceded, points.
    """
    if not tournament:
        return

    teams = Team.objects.filter(tournament=tournament)
    
    # Reset stats
    for team in teams:
        team.played = 0
        team.wins = 0
        team.draws = 0
        team.losses = 0
        team.goals_scored = 0
        team.goals_conceded = 0
        team.points = 0
    
    team_stats = {team.id: team for team in teams}
    
    matches = SingleMatch.objects.filter(home_team__tournament=tournament, status='FINISHED')

    for m in matches:
        t1 = team_stats.get(m.home_team_id)
        t2 = team_stats.get(m.away_team_id)
        
        if t1 and t2:
            update_single_match_stats(t1, m.home_goals, t2, m.away_goals)

    # Save all
    for team in team_stats.values():
        team.save()

def update_single_match_stats(team_a, score_a, team_b, score_b):
    team_a.played += 1
    team_b.played += 1
    
    team_a.goals_scored += score_a
    team_a.goals_conceded += score_b
    team_b.goals_scored += score_b
    team_b.goals_conceded += score_a
    
    if score_a > score_b:
        team_a.wins += 1
        team_a.points += 3
        team_b.losses += 1
    elif score_b > score_a:
        team_b.wins += 1
        team_b.points += 3
        team_a.losses += 1
    else:
        team_a.draws += 1
        team_a.points += 1
        team_b.draws += 1
        team_b.points += 1

def update_top_scorers(tournament):
    """
    Recalculates top scorers based on team goals.
    Since we don't have individual player goal data in the Match model,
    we assume Team Name = Player Name (as per user context).
    """
    if not tournament:
        return
        
    # Clear existing
    TopScorer.objects.filter(team__tournament=tournament).delete()
    
    teams = Team.objects.filter(tournament=tournament)
    for team in teams:
        if team.goals_scored > 0:
            TopScorer.objects.create(
                player_name=team.name,
                team=team,
                goals=team.goals_scored
            )
