import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tournament_project.settings")
django.setup()

from core.models import Tournament, Team, Match, TopScorer

def create_data():
    # Clear existing data
    print("Clearing old data...")
    Match.objects.all().delete()
    Team.objects.all().delete()
    Tournament.objects.all().delete()
    TopScorer.objects.all().delete()

    # Create Tournament
    t = Tournament.objects.create(name="KAALAPANI eFOOTBALL tournament 2025")
    print(f"Created tournament: {t.name}")

    # Create 16 Teams
    team_names = [
        "Neon Knights", "Cyber Centurions", "Plasma Panthers", "Quantum Quasars", 
        "Velocity Vipers", "Galaxy Giants", "Atomic Arrows", "Solar Strikers",
        "Lunar Legends", "Meteor Mavericks", "Stellar Spartans", "Cosmic Crusaders",
        "Nebula Ninjas", "Gravity Guardians", "Orbit Outlaws", "Void Voyagers"
    ]
    
    teams = []
    for name in team_names:
        team = Team.objects.create(
            tournament=t, 
            name=name,
            goals_scored=random.randint(5, 25),
            goals_conceded=random.randint(5, 25)
        )
        teams.append(team)
    print(f"Created {len(teams)} teams.")

    # Create Matches (Round of 16)
    # We need 8 matches for 16 teams
    random.shuffle(teams)
    r16_matches = []
    
    print("Creating Round of 16 matches...")
    for i in range(0, 16, 2):
        # Simulate two legs
        leg1_a = random.randint(0, 3)
        leg1_b = random.randint(0, 3)
        leg2_a = random.randint(0, 3)
        leg2_b = random.randint(0, 3)
        
        m = Match.objects.create(
            tournament=t,
            team_a=teams[i],
            team_b=teams[i+1],
            score_leg1_a=leg1_a,
            score_leg1_b=leg1_b,
            score_leg2_a=leg2_a,
            score_leg2_b=leg2_b,
            round='R16'
        )
        # Save again to trigger aggregate calculation and winner determination
        m.save()
        r16_matches.append(m)
        print(f"  {m.team_a} vs {m.team_b}: Agg {m.score_a}-{m.score_b} (Winner: {m.winner})")

    # Create Quarter Finals (from R16 winners)
    # We take winners from R16 matches. If a match was a draw, we pick a random winner for demo purposes.
    qf_teams = []
    for m in r16_matches:
        if m.winner:
            qf_teams.append(m.winner)
        else:
            # Handle draw for demo - pick random
            winner = random.choice([m.team_a, m.team_b])
            m.winner = winner
            m.save()
            qf_teams.append(winner)
            
    print(f"Creating Quarter Final matches for {len(qf_teams)} teams...")
    # Pair them up: Match 1 winner vs Match 2 winner, etc.
    for i in range(0, 8, 2):
        if i+1 < len(qf_teams):
            leg1_a = random.randint(0, 3)
            leg1_b = random.randint(0, 3)
            leg2_a = random.randint(0, 3)
            leg2_b = random.randint(0, 3)
            
            m = Match.objects.create(
                tournament=t,
                team_a=qf_teams[i],
                team_b=qf_teams[i+1],
                score_leg1_a=leg1_a,
                score_leg1_b=leg1_b,
                score_leg2_a=leg2_a,
                score_leg2_b=leg2_b,
                round='QF'
            )
            m.save()

    # Create Top Scorers
    player_names = ["Ace Striker", "Max Power", "Speedy Gonzalez", "Thunder Kick", "Goal Machine", "Net Buster"]
    for name in player_names:
        team = random.choice(teams)
        TopScorer.objects.create(
            player_name=name,
            team=team,
            goals=random.randint(5, 20)
        )
    print("Created Top Scorers.")

if __name__ == "__main__":
    create_data()
