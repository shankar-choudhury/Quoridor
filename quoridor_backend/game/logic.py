from collections import deque

def path_exists(game, start_pos, target_y):
    """Optimized BFS to check if a path exists to the target row."""
    visited = set()
    queue = deque([(start_pos['x'], start_pos['y'])])
    
    while queue:
        x, y = queue.popleft()
        if y == target_y:
            return True
            
        if (x, y) in visited:
            continue
        visited.add((x, y))
        
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 9 and 0 <= ny < 9:
                if not is_blocked_by_fence(game, {'x':x, 'y':y}, nx, ny):
                    queue.append((nx, ny))
    return False

def validate_fence_placement(game, player, x, y, orientation):
    """Comprehensive fence placement validation with error messages."""
    # Fence count check
    if (player == game.player1 and game.player1_fences <= 0) or \
       (player == game.player2 and game.player2_fences <= 0):
        raise ValueError("No fences remaining!")

    # Position validation
    if orientation not in ('h', 'v'):
        raise ValueError("Invalid orientation. Must be 'h' or 'v'")
    if x < 0 or x >= 8 or y < 0 or y >= 8:
        raise ValueError("Fence must be placed within bounds (0-7)")

    # Overlap check
    if any(f['x'] == x and f['y'] == y and f['orientation'] == orientation
           for f in game.fences_placed):
        raise ValueError("Fence already exists at this position")

    # Temporary placement with cleanup guarantee
    game.fences_placed.append({'x': x, 'y': y, 'orientation': orientation})
    try:
        if not (path_exists(game, game.player1_pawn, 8) and 
                path_exists(game, game.player2_pawn, 0)):
            raise ValueError("This fence would block a player's path")
    finally:
        game.fences_placed.pop()
    
    return True

def is_valid_pawn_move(game, player, new_x, new_y):
    """Validates pawn moves according to all Quoridor rules."""
    pawn = game.player1_pawn if player == game.player1 else game.player2_pawn
    opponent_pawn = game.player2_pawn if player == game.player1 else game.player1_pawn
    
    # Boundary check
    if not (0 <= new_x < 9 and 0 <= new_y < 9):
        return False
        
    dx, dy = new_x - pawn['x'], new_y - pawn['y']
    abs_dx, abs_dy = abs(dx), abs(dy)

    # Rule 2a: Standard orthogonal move
    if (abs_dx == 1 and abs_dy == 0) or (abs_dx == 0 and abs_dy == 1):
        return not is_blocked_by_fence(game, pawn, new_x, new_y)
    
    # Rule 2c: Jump over opponent
    if (abs_dx == 2 and abs_dy == 0) or (abs_dx == 0 and abs_dy == 2):
        return _validate_jump_move(game, pawn, opponent_pawn, new_x, new_y)
    
    # Rule 2d: Diagonal move when blocked
    if abs_dx == 1 and abs_dy == 1:
        return _validate_diagonal_move(game, pawn, opponent_pawn, new_x, new_y)
    
    return False

def _validate_jump_move(game, pawn, opponent_pawn, new_x, new_y):
    """Helper for validating straight jumps over opponent."""
    mid_x = (pawn['x'] + new_x) // 2
    mid_y = (pawn['y'] + new_y) // 2
    
    # Must be jumping over opponent
    if (mid_x, mid_y) != (opponent_pawn['x'], opponent_pawn['y']):
        return False
        
    # Path to opponent must be clear
    if is_blocked_by_fence(game, pawn, mid_x, mid_y):
        return False
        
    # Landing spot must be clear
    return not is_blocked_by_fence(game, opponent_pawn, new_x, new_y)

def _validate_diagonal_move(game, pawn, opponent_pawn, new_x, new_y):
    """Helper for validating diagonal moves around blocked opponents."""
    # Must be adjacent to opponent
    if abs(pawn['x'] - opponent_pawn['x']) + abs(pawn['y'] - opponent_pawn['y']) != 1:
        return False

    dir_x = opponent_pawn['x'] - pawn['x']
    dir_y = opponent_pawn['y'] - pawn['y']
    behind_x, behind_y = opponent_pawn['x'] + dir_x, opponent_pawn['y'] + dir_y

    # Calculate valid diagonals
    valid_diagonals = [
        (opponent_pawn['x'] + dir_y, opponent_pawn['y'] + dir_x),
        (opponent_pawn['x'] - dir_y, opponent_pawn['y'] - dir_x)
    ]
    
    # Check if moving to valid diagonal
    if (new_x, new_y) not in valid_diagonals:
        return False
        
    # Check landing spot
    if not (0 <= new_x < 9 and 0 <= new_y < 9):
        return False
    if (new_x, new_y) == (game.player1_pawn['x'], game.player1_pawn['y']) or \
       (new_x, new_y) == (game.player2_pawn['x'], game.player2_pawn['y']):
        return False
    
    # Either opponent is against edge or blocked by fence
    return (not (0 <= behind_x < 9 and 0 <= behind_y < 9)) or \
           is_blocked_by_fence(game, opponent_pawn, behind_x, behind_y)

def is_blocked_by_fence(game, from_pos, to_x, to_y):
    """Efficient fence blocking check using generator expressions."""
    x1, y1 = from_pos['x'], from_pos['y']
    x2, y2 = to_x, to_y

    if x1 != x2:  # Horizontal movement
        fence_x = min(x1, x2)
        return any(
            fence['orientation'] == 'v' and fence['x'] == fence_x
            and fence['y'] in {y1, y1 - 1}
            for fence in game.fences_placed
        )
    else:  # Vertical movement
        fence_y = min(y1, y2)
        return any(
            fence['orientation'] == 'h' and fence['y'] == fence_y
            and fence['x'] in {x1, x1 - 1}
            for fence in game.fences_placed
        )

def check_win_condition(game, player):
    """Determines if the player has reached their target row."""
    target_y = 8 if player == game.player1 else 0
    pawn = game.player1_pawn if player == game.player1 else game.player2_pawn
    return pawn['y'] == target_y