from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from game.models import Game
from game.logic import is_valid_pawn_move, validate_fence_placement, check_win_condition
import json

# Create your views here.

def game_view(request, game_id):
    game = Game.objects.get(id=game_id)
    return render(request, 'game/board.html', {'game': game})

@csrf_exempt
@require_http_methods(["POST"])
def move_pawn(request, game_id):
    try:
        game = Game.objects.get(id=game_id)
        data = json.loads(request.body)
        x, y = data['x'], data['y']
        
        if is_valid_pawn_move(game, request.user, x, y):
            if request.user == game.player1:
                game.player1_pawn = {'x': x, 'y': y}
            else:
                game.player2_pawn = {'x': x, 'y': y}
            
            if check_win_condition(game, request.user):
                game.winner = request.user
            
            game.current_player = game.player2 if request.user == game.player1 else game.player1
            game.save()
            
            return JsonResponse({
                'success': True,
                'game_state': get_game_state(game)
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid move'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def place_fence(request, game_id):
    try:
        game = Game.objects.get(id=game_id)
        data = json.loads(request.body)
        x, y, orientation = data['x'], data['y'], data['orientation']
        
        validate_fence_placement(game, request.user, x, y, orientation)
        
        game.fences_placed.append({
            'x': x,
            'y': y,
            'orientation': orientation
        })
        
        if request.user == game.player1:
            game.player1_fences -= 1
        else:
            game.player2_fences -= 1
            
        game.current_player = game.player2 if request.user == game.player1 else game.player1
        game.save()
        
        return JsonResponse({
            'success': True,
            'game_state': get_game_state(game)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

def get_game_state(request, game_id):
    game = Game.objects.get(id=game_id)
    return JsonResponse(get_game_state(game))

def get_game_state(game):
    return {
        'id': game.id,
        'player1': {
            'username': game.player1.username,
            'pawn': game.player1_pawn,
            'fences': game.player1_fences
        },
        'player2': {
            'username': game.player2.username,
            'pawn': game.player2_pawn,
            'fences': game.player2_fences
        },
        'current_player': {
            'id': game.current_player.id,
            'username': game.current_player.username
        },
        'fences_placed': game.fences_placed,
        'winner': {
            'id': game.winner.id if game.winner else None,
            'username': game.winner.username if game.winner else None
        }
    }

