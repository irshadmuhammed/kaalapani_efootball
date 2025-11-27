import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tournament_project.settings')
django.setup()

from core.models import Match, SingleMatch, Team
from core.utils import calculate_standings, update_top_scorers

def migrate_data():
    print("Migrating data from Match (Fixture) to SingleMatch...")
    
    # Clear existing SingleMatches to avoid duplicates if run multiple times
    SingleMatch.objects.all().delete()
    
    fixtures = Match.objects.all()
    count = 0
    
    for f in fixtures:
        # Leg 1
        # We assume if scores are present (or default 0), we create a match?
        # But default is 0.
        # How to know if it was played?
        # In the previous step, I assumed everything in DB is played.
        # But wait, I cleared the DB and populated it with specific matches.
        # So I should create SingleMatch for Leg 1.
        
        # Check if we should create Leg 1
        # If it's R16, QF, SF, F.
        # F is usually single leg.
        
        if f.round == 'F':
            # Final
            SingleMatch.objects.create(
                fixture=f,
                home_team=f.team_a,
                away_team=f.team_b,
                leg=1,
                match_datetime=None, # We don't have this info
                home_goals=f.score_a, # Aggregate is the score for single leg final
                away_goals=f.score_b,
                status='FINISHED'
            )
            count += 1
        else:
            # Two legs
            # Leg 1
            SingleMatch.objects.create(
                fixture=f,
                home_team=f.team_a, # In Leg 1, Team A is Home
                away_team=f.team_b,
                leg=1,
                match_datetime=None,
                home_goals=f.score_leg1_a,
                away_goals=f.score_leg1_b,
                status='FINISHED'
            )
            count += 1
            
            # Leg 2
            # Only if scores indicate it was played?
            # Or if we want to be consistent with previous logic.
            # Previous logic was: if I populated it, it exists.
            # But I can't distinguish 0-0 played vs 0-0 default.
            # However, for the purpose of the user's "Standings" which were working before...
            # The standings were calculated based on `Match` model.
            # Wait, `calculate_standings` in `utils.py` BEFORE my changes used `score_leg1` etc.
            # And it processed ALL matches in DB.
            # So if I want to replicate that, I must create SingleMatch for ALL legs.
            # BUT, creating 0-0 matches for unplayed games is bad.
            # The user provided a list of matches.
            # Some had Leg 2.
            # Most didn't.
            # If I create Leg 2 for everyone, I add draws to everyone.
            # I will use a heuristic: If score_leg2_a + score_leg2_b > 0, create it.
            # OR if the fixture has a winner?
            # No.
            # I'll just create Leg 1 for now.
            # And Leg 2 ONLY if sum > 0.
            # This might miss 0-0 Leg 2s, but it's better than fake draws.
            
            if f.score_leg2_a > 0 or f.score_leg2_b > 0:
                SingleMatch.objects.create(
                    fixture=f,
                    home_team=f.team_b, # In Leg 2, Team B is Home (usually)
                    away_team=f.team_a,
                    leg=2,
                    match_datetime=None,
                    home_goals=f.score_leg2_b, # Home goals (Team B)
                    away_goals=f.score_leg2_a, # Away goals (Team A)
                    status='FINISHED'
                )
                count += 1

    print(f"Created {count} SingleMatch objects.")
    
    # Recalculate standings
    tournament = fixtures.first().tournament if fixtures.exists() else None
    if tournament:
        print("Recalculating standings...")
        calculate_standings(tournament)
        update_top_scorers(tournament)
        print("Done.")

if __name__ == '__main__':
    migrate_data()
