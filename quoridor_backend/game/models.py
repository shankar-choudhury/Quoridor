from django.db import models
from django.contrib.auth.models import User

# Create your models here.

def default_player1_pawn():
    return {'x': 4, 'y': 0}

def default_player2_pawn():
    return {'x': 4, 'y': 8}

class Game(models.Model):
    # Players
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1_games')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2_games', null=True)
    current_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='current_turn')
    
    # Pawns
    player1_pawn = models.JSONField(default=default_player1_pawn)
    player2_pawn = models.JSONField(default=default_player2_pawn) 
    
    # Fences
    player1_fences = models.IntegerField(default=10)
    player2_fences = models.IntegerField(default=10)
    fences_placed = models.JSONField(default=list)  # Format: [{'x': 2, 'y': 3, 'orientation': 'h'/'v'}]
    
    # Winner
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Game {self.id}: {self.player1} vs {self.player2}"
