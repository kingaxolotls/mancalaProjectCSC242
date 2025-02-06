import sys
import math

def parse_input(input_str):
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
    stones = pits[pit_index]
    pits[pit_index] = 0
    current_pit = pit_index + 1
    while stones > 0:
        if current_pit < len(pits):
            pits[current_pit] += 1
        else:
            store += 1
            current_pit = -1
        stones -= 1
        current_pit += 1
    return pits, store    

def evaluate_state(p1_pits, p2_pits, p1_store, p2_store, player):
    score = p1_store - p2_store if player == 1 else p2_store - p1_store
    
    if player == 1:
        score = defense_calculation(p1_pits, p2_pits, score)
    else:
        score = defense_calculation(p1_pits, p2_pits, score)
    
    return score
def defense_calculation(current_pits, enemy_pits, score):
    for i in range(len(enemy_pits)):
        if enemy_pits[i] == 0 and current_pits[len(current_pits) - 1 - i] > 0:
            score -= current_pits[len(current_pits) - 1 - i]
def check_extra_turn(pits, pit_index):
    """Check whether playing the current pit ends in the player's store"""
    return len(pits) - pit_index == pits[pit_index]
def minimax(state, depth, alpha, beta, maximizing_player, player):
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
            # Checking if move grants extra turn
            extra_turn = check_extra_turn(new_p1_pits, pit_index)
            new_p1_pits, new_p1_store = make_move(new_p1_pits, new_p1_store, pit_index)
            eval = (extra_turn * 5) + minimax((new_p1_pits, new_p2_pits, new_p1_store, new_p2_store, 2), depth - 1, alpha, beta, False, player)
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
            # Checking if move grants extra turn
            extra_turn = check_extra_turn(new_p2_pits, pit_index)
            new_p2_pits, new_p2_store = make_move(new_p2_pits, new_p2_store, pit_index)
            eval = (extra_turn * 5) + minimax((new_p1_pits, new_p2_pits, new_p1_store, new_p2_store, 1), depth - 1, alpha, beta, True, player)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(state, player):
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
            eval = minimax((new_p1_pits, new_p2_pits, new_p1_store, new_p2_store, 2), depth=8, alpha=-math.inf, beta=math.inf, maximizing_player=False, player=player)
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
            eval = minimax((new_p1_pits, new_p2_pits, new_p1_store, new_p2_store, 1), depth=8, alpha=-math.inf, beta=math.inf, maximizing_player=True, player=player)
            if eval < best_value:
                best_value = eval
                best_move = pit_index
    return best_move

def should_swap(p1_pits, p2_pits, turn, player, p1_store, p2_store):
    if turn == 2 and player == 2 and p1_store > p2_store:
        return True
    return False

def main():
    input_str = sys.stdin.readline().strip()
    N, p1_pits, p2_pits, p1_store, p2_store, turn, player = parse_input(input_str)
    
    state = (p1_pits, p2_pits, p1_store, p2_store, turn)
    
    if turn == 2 and player == 2:
        p1_store > p2_store
        if should_swap(p1_pits, p2_pits, turn, player, p1_store, p2_store):
            print("PIE")
            return
    
    best_move = find_best_move(state, player)
    print(best_move + 1)

if __name__ == "__main__":
    main()
