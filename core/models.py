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
    played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    @property
    def goal_difference(self):
        return self.goals_scored - self.goals_conceded

    def __str__(self):
        return self.name

class Match(models.Model):
    ROUND_CHOICES = [
        ('R16', 'Round of 16'),
        ('QF', 'Quarter Final'),
        ('SF', 'Semi Final'),
        ('F', 'Final'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    team_a = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_as_a')
    team_b = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_as_b')
    
    # Aggregate scores (or single match score for Final)
    score_a = models.IntegerField(default=0)
    score_b = models.IntegerField(default=0)
    
    # Leg scores (for R16, QF, SF)
    score_leg1_a = models.IntegerField(default=0)
    score_leg1_b = models.IntegerField(default=0)
    score_leg2_a = models.IntegerField(default=0)
    score_leg2_b = models.IntegerField(default=0)
    
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')
    round = models.CharField(max_length=3, choices=ROUND_CHOICES)
    next_match = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_matches')

    def save(self, *args, **kwargs):
        # Calculate aggregate for two-legged matches
        if self.round != 'F':
            self.score_a = self.score_leg1_a + self.score_leg2_a
            self.score_b = self.score_leg1_b + self.score_leg2_b
            
        if self.score_a is not None and self.score_b is not None:
            if self.score_a > self.score_b:
                self.winner = self.team_a
            elif self.score_b > self.score_a:
                self.winner = self.team_b
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} ({self.round})"

class SingleMatch(models.Model):
    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('FINISHED', 'Finished'),
    ]

    fixture = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True, related_name='single_matches')
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    leg = models.IntegerField(default=1)
    match_datetime = models.DateTimeField(null=True, blank=True)
    home_goals = models.IntegerField(null=True, blank=True)
    away_goals = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UPCOMING')

    class Meta:
        verbose_name = "Match (Individual)"
        verbose_name_plural = "Matches (Individual)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync with Fixture (Match) if linked
        if self.fixture and self.status == 'FINISHED':
            if self.leg == 1:
                # Determine if home_team is team_a or team_b in fixture
                if self.home_team == self.fixture.team_a:
                    self.fixture.score_leg1_a = self.home_goals
                    self.fixture.score_leg1_b = self.away_goals
                else:
                    self.fixture.score_leg1_b = self.home_goals
                    self.fixture.score_leg1_a = self.away_goals
            elif self.leg == 2:
                if self.home_team == self.fixture.team_a:
                    self.fixture.score_leg2_a = self.home_goals
                    self.fixture.score_leg2_b = self.away_goals
                else:
                    self.fixture.score_leg2_b = self.home_goals
                    self.fixture.score_leg2_a = self.away_goals
            self.fixture.save()

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} (Leg {self.leg})"

class TopScorer(models.Model):
    player_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='scorers')
    goals = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='players/', blank=True, null=True)

    def __str__(self):
        return f"{self.player_name} ({self.goals})"
