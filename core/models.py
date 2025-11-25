from django.db import models
from django.utils.text import slugify

class Tournament(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='teams/', blank=True, null=True)
    goals_scored = models.IntegerField(default=0)
    goals_conceded = models.IntegerField(default=0)

    @property
    def goal_difference(self):
        return self.goals_scored - self.goals_conceded

    def __str__(self):
        return self.name

class Match(models.Model):
    ROUND_CHOICES = [
        ('QF', 'Quarter Final'),
        ('SF', 'Semi Final'),
        ('F', 'Final'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    team_a = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_as_a')
    team_b = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_as_b')
    score_a = models.IntegerField(default=0)
    score_b = models.IntegerField(default=0)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')
    round = models.CharField(max_length=2, choices=ROUND_CHOICES)
    next_match = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_matches')
    
    def save(self, *args, **kwargs):
        # Auto-determine winner if scores are set and different
        if self.score_a is not None and self.score_b is not None:
            if self.score_a > self.score_b:
                self.winner = self.team_a
            elif self.score_b > self.score_a:
                self.winner = self.team_b
            # If draw, winner remains None (or handle penalties logic if needed, keeping simple for now)
        
        super().save(*args, **kwargs)
        
        # Auto-advance winner to next match
        if self.winner and self.next_match:
            # Determine if this match feeds into team_a or team_b slot of next match
            # This logic is tricky without explicit "feed_slot" field. 
            # For simplicity, we can assume a convention or add a field. 
            # Let's add a logic: if next_match.team_a is None, take it. Else if next_match.team_b is None, take it.
            # But that might be race-condition prone or wrong order.
            # Better: The user (admin) sets up the bracket structure. 
            # We can leave auto-advancement for the View/Signal logic or keep it simple here.
            pass

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} ({self.round})"

class TopScorer(models.Model):
    player_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='scorers')
    goals = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='players/', blank=True, null=True)

    def __str__(self):
        return f"{self.player_name} ({self.goals})"
