import sys
import math
import random

## Diego Rodriguez, Drodri41@u.rochester.edu
## Matthew Repetsky, mrepetsk@u.rochester.edu
## Em Villa, mvilla4@u.rochester.edu
## Tristan Nygaard, tnygaard@u.rochester.edu


def parse_input(input_str):
    parts = input_str.split()
    N = int(parts[1])
    p1_pits = list(map(int, parts[2:2 + N]))
    p2_pits = list(map(int, parts[2 + N:2 + 2 * N]))
    p1_store = int(parts[2 + 2 * N])
    p2_store = int(parts[2 + 2 * N + 1])
    turn = int(parts[2 + 2 * N + 2])
    player = int(parts[2 + 2 * N + 3])
    return N, p1_pits, p2_pits, p1_store, p2_store, turn, player


def make_move(pl_pits, op_pits, store, pit_index):
    stones = pl_pits[pit_index]
    pl_pits[pit_index] = 0
    current_pit = pit_index + 1
    isPlPits = True
    while stones > 0:
        if isPlPits:
            if current_pit >= len(pl_pits):
                store += 1
                stones -= 1
                current_pit = 0
                isPlPits = False
            else:
                pl_pits[current_pit] += 1
                stones -= 1
                current_pit += 1
        else:
            if current_pit >= len(op_pits):
                current_pit = 0
                isPlPits = True
            else:
                op_pits[current_pit] += 1
                stones -= 1
                current_pit += 1
    current_pit -= 1
    if opposite_capture(pl_pits, op_pits, current_pit, isPlPits):
        store += op_pits[current_pit] + pl_pits[current_pit]
        pl_pits[current_pit] = 0
        op_pits[current_pit] = 0
    return pl_pits, op_pits, store


def opposite_capture(pl_pits, op_pits, ending_index, isPlPits):
    if isPlPits and pl_pits[ending_index] == 1 and op_pits[len(op_pits) - 1 - ending_index] > 0:
        return True
    else:
        return False


def check_extra_turn(pits, pit_index):
    stones = pits[pit_index]
    total_pits = len(pits) * 2 + 1
    final_pos = (pit_index + stones) % total_pits
    return final_pos == len(pits)

def check_empty_pits(player_pits):
    empty_pits = 0
    for pit in player_pits:
        if pit == 0:
            empty_pits += 1
    return empty_pits
def evaluation_function(player_pits, opponent_pits, player_store, opponent_store, player):
    game_phase = sum(player_pits) + sum(opponent_pits)
    store_weight = 0
    pit_stones_weight = 0
    empty_pit_weight = 0
    extra_turn_bonus = 0
    capture_bonus = 0

    if player == 2:
        player_store_, opponent_store = opponent_store, player_store
        player_store = player_store_
        player_pits, opponent_pits = opponent_pits.copy(), player_pits.copy()
        if game_phase >= 18:
            store_weight = 10
            pit_stones_weight = 2
            empty_pit_weight = 3
            extra_turn_bonus = 6
            capture_bonus = 5
        else:
            if game_phase >= 12:
                store_weight = 12
                pit_stones_weight = 2
                empty_pit_weight = 5
                extra_turn_bonus = 5
                capture_bonus = 6
            else:
                if game_phase >= 6:
                    store_weight = 14
                    pit_stones_weight = 2
                    empty_pit_weight = 7
                    extra_turn_bonus = 4
                    capture_bonus = 8
                else:
                    store_weight = 15
                    pit_stones_weight = 1
                    empty_pit_weight = 9
                    extra_turn_bonus = 3
                    capture_bonus = 9
    if player == 1:
        if game_phase >= 18:
            store_weight = 8*10
            pit_stones_weight = 3
            empty_pit_weight = 0
            extra_turn_bonus = 9
            capture_bonus = 4
        else:
            if game_phase >= 14:
                store_weight = 10*10
                pit_stones_weight = 2
                empty_pit_weight = 2
                extra_turn_bonus = 7
                capture_bonus = 5*3
            else:
                if game_phase >= 6:
                    store_weight = 11*10
                    pit_stones_weight = 2
                    empty_pit_weight = 7
                    extra_turn_bonus = 5
                    capture_bonus = 7*3
                else:
                    store_weight = 12*10
                    pit_stones_weight = 1
                    empty_pit_weight = 8*5
                    extra_turn_bonus = 4
                    capture_bonus = 8*3

    score = (player_store - opponent_store) * store_weight
    score += sum(player_pits) - sum(opponent_pits) * (pit_stones_weight)
    for i in range(len(player_pits)):
        if player_pits[i] > 0 and check_extra_turn(player_pits, i):
            score += extra_turn_bonus
    for i in range(len(player_pits)):
        if player_pits[i] > 0 and opposite_capture(player_pits, opponent_pits, i, True):
            score += capture_bonus
    score -= empty_pit_weight * check_empty_pits(player_pits)
    return score

def minimax(node, depth, og_depth, isMaximizingPlayer, alpha, beta, player):
    p1_pits, p2_pits, p1_store, p2_store = node
    if (isMaximizingPlayer and player == 1) or (not isMaximizingPlayer and player == 2):
        player_pits = p1_pits.copy()
        opponent_pits = p2_pits.copy()
        player_store = p1_store
        opponent_store = p2_store
    else:
        player_pits = p2_pits.copy()
        opponent_pits = p1_pits.copy()
        player_store = p2_store
        opponent_store = p1_store

    if depth == 0 or sum(p1_pits) == 0 or sum(p2_pits) == 0:
        return (evaluation_function(player_pits, opponent_pits, player_store, opponent_store,
                                   (1 if isMaximizingPlayer else 2)), 0)

    if isMaximizingPlayer:
        bestVal = -math.inf
        bestMove = -1

        for pit_index in range(len(player_pits)):
            if player_pits[pit_index] == 0:
                continue
            new_pl_pits = player_pits.copy()
            new_op_pits = opponent_pits.copy()
            new_pl_store = player_store
            new_op_store = opponent_store
            extra_turn = check_extra_turn(new_pl_pits, pit_index)
            new_pl_pits, new_op_pits, new_pl_store = make_move(new_pl_pits, new_op_pits, new_pl_store, pit_index)
            newNode = (new_pl_pits, new_op_pits, new_pl_store, new_op_store)
            if extra_turn:
                val, previousMove = minimax(newNode, depth - 1, og_depth, True, alpha, beta, player)
            else:
                val, previousMove = minimax(newNode, depth - 1, og_depth, False, alpha, beta, player)
            if bestVal < val:
                bestMove = pit_index
                bestVal = val
            else:
                if bestVal == val:
                    og_val = bestVal
                    bestVal = random.choice([bestVal, val])
                    if og_val != bestVal: bestMove = pit_index
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestMove
    else:
        bestVal = math.inf
        bestMove = -1

        for pit_index in range(len(opponent_pits)):
            if opponent_pits[pit_index] == 0:
                continue
            new_pl_pits = player_pits.copy()
            new_op_pits = opponent_pits.copy()
            new_pl_store = player_store
            new_op_store = opponent_store
            extra_turn = check_extra_turn(new_op_pits, pit_index)
            new_op_pits, new_pl_pits, new_op_store = make_move(new_op_pits, new_pl_pits, new_op_store, pit_index)
            newNode = (new_pl_pits, new_op_pits, new_pl_store, new_op_store)
            if extra_turn:
                val, previousMove = minimax(newNode, depth - 1, og_depth, False, alpha, beta, player)
            else:
                val, previousMove = minimax(newNode, depth - 1, og_depth, True, alpha, beta, player)
            if bestVal > val:
                bestVal = val
                bestMove = pit_index
            else:
                if bestVal == val:
                    og_val = bestVal
                    bestVal = random.choice([bestVal, val])
                    if og_val != bestVal: bestMove = pit_index
            beta = min(beta, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestMove

def should_swap(turn, player, p1_store, p2_store):
    if turn == 2 and player == 2 and p1_store > p2_store:
        return True
    return False

def main():
    input_str = sys.stdin.readline().strip()
    N, p1_pits, p2_pits, p1_store, p2_store, turn, player = parse_input(input_str)
    state = (p1_pits, p2_pits, p1_store, p2_store, turn)
    startingNode = (p1_pits, p2_pits, p1_store, p2_store)

    if turn == 2 and player == 2:
        if should_swap(turn, player, p1_store, p2_store):
            print("PIE")
            return

    best_value, best_move = minimax(startingNode, 8, 8, True, -math.inf, math.inf, player)

    print(best_move + 1)

if __name__ == "__main__":
    main()
