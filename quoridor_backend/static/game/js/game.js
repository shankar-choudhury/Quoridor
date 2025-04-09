let currentMode = 'move';
let selectedCell = null;
let gameState = {};
let csrfToken = '';

function initGame(gameId, token, initialState) {
    csrfToken = token;
    gameState = {
        id: gameId,
        ...initialState,
        fences_placed: initialState.fencesPlaced,
        current_player: { username: initialState.currentPlayer }
    };
    
    // Initialize UI with the initial state
    updateUI(gameState);
    
    // Set up event listeners
    setupEventListeners();
    
    // Start polling for game updates
    setInterval(() => fetchGameState(gameId), 3000);
}

function setupEventListeners() {
    // Cell click handling
    document.querySelectorAll('.cell').forEach(cell => {
        cell.addEventListener('click', () => handleCellClick(cell));
    });
    
    // Mode buttons
    document.getElementById('move-mode').addEventListener('click', () => {
        currentMode = 'move';
        toggleActiveButton('move-mode');
        document.getElementById('fence-orientation').disabled = true;
    });
    
    document.getElementById('fence-mode').addEventListener('click', () => {
        currentMode = 'fence';
        toggleActiveButton('fence-mode');
        document.getElementById('fence-orientation').disabled = false;
    });
}

async function handleCellClick(cell) {
    const x = parseInt(cell.dataset.x);
    const y = parseInt(cell.dataset.y);
    
    if (currentMode === 'move') {
        await makeMove(x, y);
    } else {
        await placeFence(x, y);
    }
}

async function makeMove(x, y) {
    try {
        const response = await fetch(`/api/game/${gameState.id}/move/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ x, y })
        });
        
        const result = await response.json();
        if (result.success) {
            gameState = result.game_state;
            updateUI(gameState);
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
    }
}

async function placeFence(x, y) {
    const orientation = document.getElementById('fence-orientation').value;
    
    try {
        const response = await fetch(`/api/game/${gameState.id}/fence/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ x, y, orientation })
        });
        
        const result = await response.json();
        if (result.success) {
            gameState = result.game_state;
            updateUI(gameState);
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
    }
}

async function fetchGameState(gameId) {
    try {
        const response = await fetch(`/api/game/${gameId}/`);
        const newState = await response.json();
        
        // Only update if state changed
        if (JSON.stringify(gameState) !== JSON.stringify(newState)) {
            gameState = newState;
            updateUI(gameState);
        }
    } catch (error) {
        console.error('Failed to fetch game state:', error);
    }
}

function updateUI(state) {
    // Update pawn positions
    document.querySelectorAll('.pawn').forEach(p => p.remove());
    
    const p1Cell = document.getElementById(`cell-${state.player1.pawn.x}-${state.player1.pawn.y}`);
    if (p1Cell) {
        p1Cell.innerHTML = '<div class="pawn player1"></div>';
    }
    
    const p2Cell = document.getElementById(`cell-${state.player2.pawn.x}-${state.player2.pawn.y}`);
    if (p2Cell) {
        p2Cell.innerHTML = '<div class="pawn player2"></div>';
    }
    
    // Update fences
    document.querySelectorAll('.fence').forEach(f => f.classList.remove('h-fence', 'v-fence'));
    
    state.fences_placed.forEach(fence => {
        const cell = document.getElementById(`cell-${fence.x}-${fence.y}`);
        if (cell) {
            cell.classList.add(`${fence.orientation}-fence`);
        }
    });
    
    // Update game info
    document.getElementById('current-player').textContent = state.current_player.username;
    document.getElementById('p1-fences').textContent = state.player1.fences;
    document.getElementById('p2-fences').textContent = state.player2.fences;
    
    if (state.winner) {
        showMessage(`${state.winner.username} wins the game!`, 'success');
        // Disable further moves
        document.querySelectorAll('.cell').forEach(c => c.style.pointerEvents = 'none');
    }
}

function toggleActiveButton(activeId) {
    document.getElementById('move-mode').classList.remove('active');
    document.getElementById('fence-mode').classList.remove('active');
    document.getElementById(activeId).classList.add('active');
}

function showMessage(message, type) {
    const msgElement = document.getElementById('game-message');
    msgElement.textContent = message;
    msgElement.className = type;
    
    // Auto-hide messages after 5 seconds
    if (type !== 'error') {
        setTimeout(() => {
            msgElement.textContent = '';
            msgElement.className = '';
        }, 5000);
    }
}