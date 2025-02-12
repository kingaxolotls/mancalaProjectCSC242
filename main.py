import sys
import math


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


def evaluation_function(player_pits, opponent_pits, player_store, opponent_store, player):
    if player == 2:
        player_store_, opponent_store = opponent_store, player_store
        player_store = player_store_
        player_pits, opponent_pits = opponent_pits.copy(), player_pits.copy()

    store_weight = 10
    extra_turn_bonus = 5
    capture_bonus = 7
    score = (player_store - opponent_store) * store_weight
    score += sum(player_pits) - sum(opponent_pits)
    for i in range(len(player_pits)):
        if player_pits[i] > 0 and check_extra_turn(player_pits, i):
            score += extra_turn_bonus
    for i in range(len(player_pits)):
        if player_pits[i] > 0 and opposite_capture(player_pits, opponent_pits, i, True):
            score += capture_bonus

    return score

def minimax(node, depth, isMaximizingPlayer, alpha, beta, player):
    p1_pits, p2_pits, p1_store, p2_store = node
    # Determine which side is "player" and which is opponent.
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

    # Terminal condition: depth 0 or one side empty
    if depth == 0 or sum(p1_pits) == 0 or sum(p2_pits) == 0:
        # Note: The evaluation function uses a player number of 1 or 2.
        return evaluation_function(player_pits, opponent_pits, player_store, opponent_store,
                                   (1 if isMaximizingPlayer else 2))

    if isMaximizingPlayer:
        bestVal = -math.inf
        # Loop over the player's pits (depending on perspective)
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
                val = minimax(newNode, depth - 1, True, alpha, beta, player)
            else:
                val = minimax(newNode, depth - 1, False, alpha, beta, player)
            bestVal = max(bestVal, val)
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                break
        return bestVal
    else:
        bestVal = math.inf
        # Loop over the opponent's pits
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
                val = minimax(newNode, depth - 1, False, alpha, beta, player)
            else:
                val = minimax(newNode, depth - 1, True, alpha, beta, player)
            bestVal = min(bestVal, val)
            beta = min(beta, bestVal)
            if beta <= alpha:
                break
        return bestVal


def get_best_move(p1_pits, p2_pits, p1_store, p2_store, player, depth):
    best_val = -math.inf
    best_move = -1
    # Determine which pits to iterate over at the root based on the player.
    if player == 1:
        pits = p1_pits
    else:
        pits = p2_pits

    # Try each possible move
    for pit_index in range(len(pits)):
        if pits[pit_index] == 0:
            continue
        if player == 1:
            new_p1_pits = p1_pits.copy()
            new_p2_pits = p2_pits.copy()
            new_p1_store = p1_store
            extra_turn = check_extra_turn(new_p1_pits, pit_index)
            new_p1_pits, new_p2_pits, new_p1_store = make_move(new_p1_pits, new_p2_pits, new_p1_store, pit_index)
            new_state = (new_p1_pits, new_p2_pits, new_p1_store, p2_store)
        else:
            new_p2_pits = p2_pits.copy()
            new_p1_pits = p1_pits.copy()
            new_p2_store = p2_store
            extra_turn = check_extra_turn(new_p2_pits, pit_index)
            new_p2_pits, new_p1_pits, new_p2_store = make_move(new_p2_pits, new_p1_pits, new_p2_store, pit_index)
            new_state = (new_p1_pits, new_p2_pits, p1_store, new_p2_store)
        # If extra turn, the same player continues as the maximizing player.
        if extra_turn:
            val = minimax(new_state, depth - 1, True, -math.inf, math.inf, player)
        else:
            val = minimax(new_state, depth - 1, False, -math.inf, math.inf, player)
        if val > best_val:
            best_val = val
            best_move = pit_index
    return best_move


def should_swap(turn, player, p1_store, p2_store):
    if turn == 2 and player == 2 and p1_store > p2_store:
        return True
    return False


def main():
    input_str = sys.stdin.readline().strip()
    N, p1_pits, p2_pits, p1_store, p2_store, turn, player = parse_input(input_str)
    state = (p1_pits, p2_pits, p1_store, p2_store, turn)

    if turn == 2 and player == 2:
        if should_swap(turn, player, p1_store, p2_store):
            print("PIE")
            return

    # Use the helper to choose the best move (pit index)
    best_move = get_best_move(p1_pits, p2_pits, p1_store, p2_store, player, 7)
    # Adding 1 converts from 0-based indexing to the expected output
    print(best_move + 1)


if __name__ == "__main__":
    main()
