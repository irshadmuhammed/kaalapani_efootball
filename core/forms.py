from django import forms
from .models import SingleMatch, Team, Tournament
from django.core.exceptions import ValidationError
from django.db.models import Q

class MatchForm(forms.ModelForm):
    # team_a_name = forms.CharField(label="Team A", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type team name...'}))
    # team_b_name = forms.CharField(label="Team B", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type team name...'}))
    
    class Meta:
        model = SingleMatch
        fields = ['home_team', 'away_team', 'leg', 'match_datetime', 'home_goals', 'away_goals', 'status']
        widgets = {
            'home_team': forms.Select(attrs={'class': 'form-control'}),
            'away_team': forms.Select(attrs={'class': 'form-control'}),
            'leg': forms.NumberInput(attrs={'class': 'form-control'}),
            'match_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'home_goals': forms.NumberInput(attrs={'class': 'form-control'}),
            'away_goals': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        home_team = cleaned_data.get('home_team')
        away_team = cleaned_data.get('away_team')
        
        if home_team and away_team and home_team == away_team:
            raise ValidationError("Home Team and Away Team cannot be the same.")
            
        return cleaned_data


