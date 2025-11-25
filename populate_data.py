import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tournament_project.settings")
django.setup()

from core.models import Tournament, Team, Match, TopScorer

def create_data():
    # Create Tournament
    t, created = Tournament.objects.get_or_create(name="Turbo League 2024")
    if created:
        print(f"Created tournament: {t.name}")
    else:
        print(f"Tournament {t.name} already exists")

    # Create Teams
    team_names = ["Neon Knights", "Cyber Centurions", "Plasma Panthers", "Quantum Quasars", 
                  "Velocity Vipers", "Galaxy Giants", "Atomic Arrows", "Solar Strikers"]
    teams = []
    for name in team_names:
        team, created = Team.objects.get_or_create(tournament=t, name=name)
        if created:
            team.goals_scored = random.randint(5, 20)
            team.goals_conceded = random.randint(5, 20)
            team.save()
        teams.append(team)
    print(f"Ensured {len(teams)} teams.")

    # Create Matches (Quarter Finals)
    # We need 4 matches for 8 teams
    if not Match.objects.filter(tournament=t, round='QF').exists():
        random.shuffle(teams)
        matches = []
        for i in range(0, 8, 2):
            m = Match.objects.create(
                tournament=t,
                team_a=teams[i],
                team_b=teams[i+1],
                score_a=random.randint(0, 5),
                score_b=random.randint(0, 5),
                round='QF'
            )
            matches.append(m)
        print("Created QF matches.")
        
        # Create Semi Finals (Empty for now, or populated based on winners)
        # For demo, let's just create QF matches.
    else:
        print("Matches already exist.")

    # Create Top Scorers
    if not TopScorer.objects.exists():
        player_names = ["Ace Striker", "Max Power", "Speedy Gonzalez", "Thunder Kick"]
        for name in player_names:
            team = random.choice(teams)
            TopScorer.objects.create(
                player_name=name,
                team=team,
                goals=random.randint(3, 15)
            )
        print("Created Top Scorers.")

if __name__ == "__main__":
    create_data()
