from django import forms
from .models import Match, Team, Tournament
from django.core.exceptions import ValidationError
from django.db.models import Q

class MatchForm(forms.ModelForm):
    team_a_name = forms.CharField(label="Team A", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type team name...'}))
    team_b_name = forms.CharField(label="Team B", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type team name...'}))
    
    class Meta:
        model = Match
        fields = ['round', 'score_leg1_a', 'score_leg1_b', 'score_leg2_a', 'score_leg2_b']
        widgets = {
            'round': forms.Select(attrs={'class': 'form-control'}),
            'score_leg1_a': forms.NumberInput(attrs={'class': 'form-control'}),
            'score_leg1_b': forms.NumberInput(attrs={'class': 'form-control'}),
            'score_leg2_a': forms.NumberInput(attrs={'class': 'form-control'}),
            'score_leg2_b': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.team_a:
                self.fields['team_a_name'].initial = self.instance.team_a.name
            if self.instance.team_b:
                self.fields['team_b_name'].initial = self.instance.team_b.name

    def clean(self):
        cleaned_data = super().clean()
        team_a_name = cleaned_data.get('team_a_name')
        team_b_name = cleaned_data.get('team_b_name')
        
        if not team_a_name or not team_b_name:
            return cleaned_data

        # Fuzzy match teams
        team_a = self._get_fuzzy_team(team_a_name)
        team_b = self._get_fuzzy_team(team_b_name)
        
        if not team_a:
            self.add_error('team_a_name', f"Could not find team matching '{team_a_name}'")
        if not team_b:
            self.add_error('team_b_name', f"Could not find team matching '{team_b_name}'")
            
        if team_a and team_b:
            if team_a == team_b:
                raise ValidationError("Team A and Team B cannot be the same.")
            
            cleaned_data['team_a'] = team_a
            cleaned_data['team_b'] = team_b
            
            # Check for duplicates (excluding self if editing)
            # We consider a duplicate if same teams meet in same round
            # Note: Leg is part of the match object fields in this form, but model stores both legs in one object usually?
            # Wait, the model has score_leg1 and score_leg2.
            # So one Match object represents the whole fixture (both legs).
            # The user's prompt said "Leg Number (1 or 2)" in the form.
            # This implies they want to enter ONE leg at a time?
            # "Add Match Result... Leg Number (1 or 2)... Goals A... Goals B"
            # If I follow the prompt strictly, I should allow updating specific legs of a match.
            # BUT my model stores both legs in one object.
            # So if I add "Leg 1", I create the match.
            # If I add "Leg 2", I should UPDATE the existing match.
            
            # Let's check if a match exists between these teams.
            existing_match = Match.objects.filter(
                (Q(team_a=team_a) & Q(team_b=team_b)) | 
                (Q(team_a=team_b) & Q(team_b=team_a))
            ).exclude(pk=self.instance.pk if self.instance else None).first()
            
            if existing_match:
                # If match exists, we should probably tell the user to EDIT it instead of creating a new one?
                # Or if this is an "Add" form, maybe we auto-update?
                # The prompt says "Prevent duplicates (same teams + same leg)".
                # Since my model has both legs, "same teams" is the constraint.
                # I will allow editing via the "Edit" page.
                # If they try to add a new match for existing teams, I should warn them.
                # But maybe they want to add a match for a different round?
                # The form has 'round'.
                round_val = cleaned_data.get('round')
                if existing_match.round == round_val:
                     raise ValidationError(f"A match between {team_a} and {team_b} already exists in {existing_match.get_round_display()}. Please edit it instead.")
            
        return cleaned_data

    def _get_fuzzy_team(self, name):
        # Simple normalization
        norm_name = name.strip().lower()
        teams = Team.objects.all()
        
        # Exact match
        for team in teams:
            if team.name.lower() == norm_name:
                return team
                
        # Substring match
        for team in teams:
            if norm_name in team.name.lower():
                return team
                
        return None

    def save(self, commit=True):
        match = super().save(commit=False)
        match.team_a = self.cleaned_data['team_a']
        match.team_b = self.cleaned_data['team_b']
        
        # Ensure tournament is set
        if not match.tournament_id:
            match.tournament = Tournament.objects.first()
            
        if commit:
            match.save()
        return match
