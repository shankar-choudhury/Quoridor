from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from game.models import Game
from game.logic import (
    is_valid_pawn_move,
    check_win_condition,
    validate_fence_placement,
    is_blocked_by_fence
)

class Command(BaseCommand):
    help = 'Play Quoridor via command line'

    def handle(self, *args, **kwargs):
        self.stdout.write("Game starting...")
        # Setup game
        player1 = User.objects.get(username='player1')
        player2 = User.objects.get(username='player2')
        game = Game.objects.create(
            player1=player1,
            player2=player2,
            current_player=player1,
            player1_pawn={'x': 4, 'y': 0},
            player2_pawn={'x': 4, 'y': 8}
        )

        while not game.winner:
            self.print_board(game)
            player = game.current_player
            pawn = game.player1_pawn if player == player1 else game.player2_pawn
            fences_left = game.player1_fences if player == player1 else game.player2_fences
            
            self.stdout.write(
                f"\n{player.username}'s turn\n"
                f"Your pawn: ({pawn['x']}, {pawn['y']})\n"
                f"Fences remaining: {fences_left}\n"
            )

            # Get move type
            while True:
                choice = input("Move pawn (m) or place fence (f)? ").lower()
                if choice in ('m', 'f'):
                    break
                self.stdout.write("Please enter 'm' or 'f'")

            try:
                if choice == 'm':
                    x, y = map(int, input("Enter new pawn position (x y): ").split())
                    if is_valid_pawn_move(game, player, x, y):
                        if player == player1:
                            game.player1_pawn = {'x': x, 'y': y}
                        else:
                            game.player2_pawn = {'x': x, 'y': y}
                    else:
                        raise ValueError("Invalid move!")

                elif choice == 'f':
                    if fences_left <= 0:
                        raise ValueError("No fences remaining!")
                    
                    x, y = map(int, input("Enter fence position (x y): ").split())
                    orientation = input("Enter orientation (h/v): ").lower()
                    
                    if orientation not in ('h', 'v'):
                        raise ValueError("Orientation must be 'h' or 'v'")
                    
                    validate_fence_placement(game, player, x, y, orientation)
                    
                    game.fences_placed.append({
                        'x': x,
                        'y': y,
                        'orientation': orientation
                    })
                    
                    if player == player1:
                        game.player1_fences -= 1
                    else:
                        game.player2_fences -= 1

                # Check win condition
                if check_win_condition(game, player):
                    game.winner = player
                    game.save()
                    self.print_board(game)
                    self.stdout.write(self.style.SUCCESS(f"\n{player.username} wins!"))
                    break

                # Switch player
                game.current_player = player2 if player == player1 else player1
                game.save()

            except ValueError as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
                continue

    def print_board(self, game):
        """Enhanced board display showing pawns and fences"""
        # Initialize empty board
        board = [[ '· ' for _ in range(9)] for _ in range(9)]
        
        # Place pawns
        board[game.player1_pawn['y']][game.player1_pawn['x']] = 'P1'
        board[game.player2_pawn['y']][game.player2_pawn['x']] = 'P2'
        
        # Add horizontal fences
        for fence in game.fences_placed:
            if fence['orientation'] == 'h':
                y = fence['y']
                for x in range(fence['x'], fence['x'] + 2):
                    if 0 <= x < 8 and 0 <= y < 9:
                        board[y][x] = board[y][x].replace(' ', '═')
        
        # Add vertical fences
        for fence in game.fences_placed:
            if fence['orientation'] == 'v':
                x = fence['x']
                for y in range(fence['y'], fence['y'] + 2):
                    if 0 <= x < 9 and 0 <= y < 8:
                        board[y][x] = board[y][x].replace(' ', '║')
        
        # Print the board with coordinates
        print("\n   " + " ".join(f"{i} " for i in range(9)))
        for y in range(9):
            print(f"{y} ", end="")
            for x in range(9):
                print(board[y][x], end="")
            print()