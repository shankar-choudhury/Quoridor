from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def default_player1_pawn():
    return {'x': 4, 'y': 0}

def default_player2_pawn():
    return {'x': 4, 'y': 8}

class Game(models.Model):
    # Players
    player1 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='player1_games'
    )
    player2 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='player2_games', 
        null=True,
        blank=True  # Allow empty for game creation flow
    )
    current_player = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='current_turn'
    )
    
    # Pawns
    player1_pawn = models.JSONField(default=default_player1_pawn)
    player2_pawn = models.JSONField(default=default_player2_pawn) 
    
    # Fences
    player1_fences = models.IntegerField(default=10)
    player2_fences = models.IntegerField(default=10)
    fences_placed = models.JSONField(
        default=list,
        blank=True,
        help_text="List of dictionaries with x,y,orientation"
    )
    
    # Winner
    winner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        related_name='won_games'
    )

    def __str__(self):
        return f"Game {self.id}: {self.player1} vs {self.player2 or 'AI'}"

    def clean(self):
        """Validate game state before saving"""
        if self.current_player not in [self.player1, self.player2]:
            raise ValidationError("Current player must be player1 or player2")
        
        if self.winner and self.winner not in [self.player1, self.player2]:
            raise ValidationError("Winner must be player1 or player2")

    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation on save
        super().save(*args, **kwargs)

    @classmethod
    def create_default_game(cls, username1='player1', username2='player2'):
        """Helper method to create a game with default players"""
        player1, _ = User.objects.get_or_create(username=username1)
        player2, _ = User.objects.get_or_create(username=username2)
        
        return cls.objects.create(
            player1=player1,
            player2=player2,
            current_player=player1
        )

    def get_absolute_url(self):
        """For WebUI compatibility - links to game detail page"""
        from django.urls import reverse
        return reverse('game', kwargs={'game_id': self.id})

    def to_dict(self):
        """Serialization method for WebUI API"""
        return {
            'id': self.id,
            'players': {
                'player1': self.player1.username,
                'player2': self.player2.username if self.player2 else None
            },
            'pawns': {
                'player1': self.player1_pawn,
                'player2': self.player2_pawn
            },
            'fences': {
                'player1': self.player1_fences,
                'player2': self.player2_fences,
                'placed': self.fences_placed
            },
            'current_player': self.current_player.username,
            'winner': self.winner.username if self.winner else None
        }
