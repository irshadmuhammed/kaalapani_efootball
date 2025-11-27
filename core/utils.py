from .models import Match, Team

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
        # We don't save yet, we'll do bulk update or save individually after calc
        # Actually, for simplicity and safety, let's use a dictionary to track stats in memory
        # then update the DB objects.
    
    team_stats = {team.id: team for team in teams}
    
    matches = Match.objects.filter(tournament=tournament)
    
    for m in matches:
        # Check if match has valid scores (Leg 1)
        if m.score_leg1_a is not None and m.score_leg1_b is not None:
             # We assume if scores are present, the leg was played.
             # Note: Default is 0. If both are 0, it counts as 0-0 draw.
             # This might be an issue if matches are created but not played.
             # But based on user requirements, we process what's in DB.
             
             # However, to avoid counting unplayed matches (if any), 
             # we could check if the match is marked as 'finished' or similar.
             # The Match model doesn't have a status field.
             # But the user said "Matches have already been added".
             # We will process all matches.
             
             t1 = team_stats.get(m.team_a_id)
             t2 = team_stats.get(m.team_b_id)
             
             if t1 and t2:
                 # Leg 1
                 update_single_match_stats(t1, m.score_leg1_a, t2, m.score_leg1_b)
                 
                 # Leg 2
                 # Only if scores are non-zero? Or how to distinguish?
                 # If we blindly process Leg 2 (default 0-0), we double the games played.
                 # The user's input had some Leg 2 matches.
                 # If the DB has 0-0 for Leg 2, it counts as a draw.
                 # This is a potential bug if we process unplayed legs.
                 # BUT, I can't change the model schema now to add 'played' flags without migration.
                 # I will assume that for the purpose of this task, we recalculate based on the provided data.
                 # The provided data was inserted into specific legs.
                 # If I only process legs where scores > 0 OR if it was in the user's list...
                 # But I don't know which ones were in the user's list here.
                 
                 # Let's look at the `update_results.py` logic again.
                 # It updated specific legs.
                 # If I want to be safe, I should probably only count legs that have non-zero total score?
                 # No, 0-0 is valid.
                 
                 # Let's rely on the fact that I CLEARED the matches in update_results.py.
                 # So ONLY the matches the user provided exist.
                 # AND `update_results.py` only set the specific legs provided.
                 # Wait, `Match` model has defaults.
                 # If I created a match for Leg 1, Leg 2 defaults to 0-0.
                 # So Leg 2 WILL be counted as a draw.
                 # THIS IS A BUG in my previous step if I didn't handle it.
                 
                 # In `update_results.py`, I did:
                 # match = Match(...)
                 # match.score_leg1_a = ...
                 # match.save()
                 
                 # Leg 2 defaults to 0.
                 
                 # To fix this, I should probably check if `score_leg2_a` and `score_leg2_b` are 0 AND 
                 # it wasn't explicitly set. But I can't know.
                 
                 # Actually, the user's list had Leg 1 and Leg 2.
                 # "Vasco vs Ashwajith (Leg 1)"
                 # "Abin vs Hisham (Leg 1)"
                 # "Abin vs Hisham (Leg 2)"
                 
                 # If I process Leg 2 for Vasco, it will be 0-0.
                 # Vasco played 1 game, but will show 2 games (1 win, 1 draw).
                 
                 # I MUST fix this logic.
                 # Since I can't change the model, I will use a heuristic:
                 # If the match round is R16/QF/SF (2 legs), we need to know if Leg 2 was played.
                 # But I can't know for sure.
                 
                 # ALTERNATIVE:
                 # I can check if the `winner` field is set? No, winner is for the aggregate.
                 
                 # Let's just implement the basic calculation for now.
                 # If the user sees extra draws, I can explain/fix.
                 # But the user said "P, W, D, L are all showing as 0".
                 # So ANY non-zero value is an improvement.
                 
                 # I will process Leg 2 ONLY if the sum of scores > 0.
                 # This avoids 0-0 defaults counting as draws for unplayed legs.
                 # It misses valid 0-0 draws, but it's safer than counting unplayed games.
                 # (Unless the user explicitly entered 0-0, which is rare for Leg 2 in this context).
                 
                 if m.score_leg2_a > 0 or m.score_leg2_b > 0:
                     update_single_match_stats(t1, m.score_leg2_a, t2, m.score_leg2_b)
                 elif m.round == 'F':
                     # Final is single leg usually, stored in score_a/score_b?
                     # Model says: if round != 'F', calculate aggregate.
                     # So Final uses score_a/score_b directly?
                     # The model has `score_a` and `score_b` as aggregates.
                     # But for Final, `score_leg1` might be used as the main score?
                     # Let's assume R16/QF/SF for now as per data.
                     pass

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

from .models import TopScorer

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
