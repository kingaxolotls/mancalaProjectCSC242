import sys
import math

def parse_input(input_str):
    """Parse the input string into game state variables."""
    parts = input_str.split()
    N = int(parts[1])
    p1_pits = list(map(int, parts[2:2+N]))
    p2_pits = list(map(int, parts[2+N:2+2*N]))
    p1_store = int(parts[2+2*N])
    p2_store = int(parts[2+2*N+1])
    turn = int(parts[2+2*N+2])
    player = int(parts[2+2*N+3])
    
    return N, p1_pits, p2_pits, p1_store, p2_store, turn, player

def make_move(pits, store, pit_index):
    """Simulate a move in Mancala."""
    stones = pits[pit_index]
    pits[pit_index] = 0
    current_pit = pit_index + 1
    while stones > 0:
        if current_pit < len(pits):
            pits[current_pit] += 1
        else:
            store += 1
            current_pit = -1  # Reset to start of pits
        stones -= 1
        current_pit += 1
    return pits, store

def evaluate_state(p1_pits, p2_pits, p1_store, p2_store, player):
    """Evaluate the game state for the given player."""
    if player == 1:
        return p1_store - p2_store
    else:
        return p2_store - p1_store

def minimax(state, depth, alpha, beta, maximizing_player, player):
    """Minimax algorithm with alpha-beta pruning."""
    p1_pits, p2_pits, p1_store, p2_store, turn = state
    
    if depth == 0 or sum(p1_pits) == 0 or sum(p2_pits) == 0:
        return evaluate_state(p1_pits, p2_pits, p1_store, p2_store, player)
    
    if maximizing_player:
        max_eval = -math.inf
        for pit_index in range(len(p1_pits)):
            if p1_pits[pit_index] == 0:
                continue
            new_p1_pits = p1_pits.copy()
            new_p2_pits = p2_pits.copy()
            new_p1_store = p1_store
            new_p2_store = p2_store
            new_p1_pits, new_p1_store = make_move(new_p1_pits, new_p1_store, pit_index)
            eval = minimax((new_p1_pits, new_p2_pits, new_p1_store, new_p2_store, 2), depth - 1, alpha, beta, False, player)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for pit_index in range(len(p2_pits)):
            if p2_pits[pit_index] == 0:
                continue
            new_p1_pits = p1_pits.copy()
            new_p2_pits = p2_pits.copy()
            new_p1_store = p1_store
            new_p2_store = p2_store
            new_p2_pits, new_p2_store = make_move(new_p2_pits, new_p2_store, pit_index)
            eval = minimax((new_p1_pits, new_p2_pits, new_p1_store, new_p2_store, 1), depth - 1, alpha, beta, True, player)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(state, player):
    """Find the best move using the Minimax algorithm."""
    p1_pits, p2_pits, p1_store, p2_store, turn = state
    best_move = None
    best_value = -math.inf if player == 1 else math.inf
    
    if player == 1:
        for pit_index in range(len(p1_pits)):
            if p1_pits[pit_index] == 0:
                continue
            new_p1_pits = p1_pits.copy()
            new_p2_pits = p2_pits.copy()
            new_p1_store = p1_store
            new_p2_store = p2_store
            new_p1_pits, new_p1_store = make_move(new_p1_pits, new_p1_store, pit_index)
            eval = minimax((new_p1_pits, new_p2_pits, new_p1_store, new_p2_store, 2), depth=3, alpha=-math.inf, beta=math.inf, maximizing_player=False, player=player)
            if eval > best_value:
                best_value = eval
                best_move = pit_index
    else:
        for pit_index in range(len(p2_pits)):
            if p2_pits[pit_index] == 0:
                continue
            new_p1_pits = p1_pits.copy()
            new_p2_pits = p2_pits.copy()
            new_p1_store = p1_store
            new_p2_store = p2_store
            new_p2_pits, new_p2_store = make_move(new_p2_pits, new_p2_store, pit_index)
            eval = minimax((new_p1_pits, new_p2_pits, new_p1_store, new_p2_store, 1), depth=3, alpha=-math.inf, beta=math.inf, maximizing_player=True, player=player)
            if eval < best_value:
                best_value = eval
                best_move = pit_index
    return best_move

def should_swap(p1_pits, p2_pits):
    """Determine if the second player should swap the board."""
    # Example heuristic: Swap if the opponent has more stones in their pits.
    return sum(p1_pits) > sum(p2_pits)

def main():
    """Main function to handle input and output."""
    input_str = sys.stdin.readline().strip()
    N, p1_pits, p2_pits, p1_store, p2_store, turn, player = parse_input(input_str)
    
    state = (p1_pits, p2_pits, p1_store, p2_store, turn)
    
    # Print the game state being sent to the player
    print(f"Sending STATE {N} {' '.join(map(str, p1_pits))} {' '.join(map(str, p2_pits))} {p1_store} {p2_store} {turn} {player} to player {player}")
    
    # Handle "PIE" rule for the second player on the first turn
    if turn == 1 and player == 2:
        if should_swap(p1_pits, p2_pits):
            print("PIE")
            return
    
    # Find and output the best move
    best_move = find_best_move(state, player)
    print(f"Turn {turn}, Player {player} move: {best_move + 1}")  # Pits are 1-indexed in output

if __name__ == "__main__":
    main()
