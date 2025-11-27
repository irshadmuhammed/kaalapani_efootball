import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tournament_project.settings")
django.setup()

from core.models import Team

teams = Team.objects.all()
print(f"Found {teams.count()} teams:")
for team in teams:
    print(f"ID: {team.id}, Name: '{team.name}'")
