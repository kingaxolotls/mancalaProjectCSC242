import sys
import random

# Global settings.
capture_empty_pots = False
capture_own_pieces = False
ai_move_depth = 8

# Initial board state.
initial_board = {
    'one': [3] * 6,
    'two': [3] * 6,
    'onePot': 0,
    'twoPot': 0
}

# Mapping to get the other player.
next_player = {
    'one': 'two',
    'two': 'one'
}


def copy_board(board):
    """Return a deep copy of the board."""
    return {
        'one': board['one'][:],
        'two': board['two'][:],
        'onePot': board['onePot'],
        'twoPot': board['twoPot']
    }


def can_capture(player, board_side):
    """Determine if a capture is allowed."""
    return capture_own_pieces or (player == board_side)


def update_board(board, move, player):
    """
    Update the board by applying a move.
    
    Returns a tuple: (new_board, new_player)
    """
    number = board[player][move]
    board_side = player
    new_board = copy_board(board)
    new_board[player][move] = 0
    move += 1

    while number > 0:
        change_player = True

        # Place a seed into each hollow in turn.
        while move < 6 and number > 0:
            new_board[board_side][move] += 1
            move += 1
            number -= 1

        # Placing a seed into the player's pot.
        if number > 0:
            new_board[f"{board_side}Pot"] += 1
            number -= 1
            change_player = False

        # Capturing from the opponent.
        elif new_board[board_side][move - 1] == 1 and can_capture(player, board_side):
            other_side_pot = 6 - move
            other_side = next_player[board_side]
            other_side_pot_amount = new_board[other_side][other_side_pot]
            if capture_empty_pots or other_side_pot_amount > 0:
                new_board[other_side][other_side_pot] = 0
                new_board[board_side][move - 1] = 0
                new_board[f"{board_side}Pot"] += other_side_pot_amount + 1

        board_side = next_player[board_side]
        move = move - 6

    new_player = next_player[player] if change_player else player
    return new_board, new_player


def print_board(board):
    """Print the board state in a user‐friendly way."""
    # Top row: player two's hollows in reverse order.
    line_one = "  " + " ".join(str(board['two'][i]) for i in range(5, -1, -1))
    # Middle row: the two pots.
    line_two = f"{board['twoPot']}" + " " * 12 + f"{board['onePot']}"
    # Bottom row: player one's hollows.
    line_three = "  " + " ".join(str(x) for x in board['one'])
    print(line_one)
    print(line_two)
    print(line_three)


def array_eq(a1, a2):
    return len(a1) == len(a2) and all(x == y for x, y in zip(a1, a2))


def board_eq(board1, board2):
    return (board1['onePot'] == board2['onePot'] and
            board1['twoPot'] == board2['twoPot'] and
            array_eq(board1['one'], board2['one']) and
            array_eq(board1['two'], board2['two']))


def get_random_move(board, player):
    """Return a random valid move (an index 0-5 where the hollow is not empty)."""
    while True:
        move = random.randrange(6)
        if board[player][move] != 0:
            return move


def get_moves(board, player):
    """Return a list of all move indices (0-5) that are valid (non-zero seeds)."""
    return [i for i in range(6) if board[player][i] != 0]


def score(board, player):
    """Return the difference in pots for a given player."""
    return board[f"{player}Pot"] - board[f"{next_player[player]}Pot"]


def final_score(board, player):
    """Calculate the final score, including seeds in hollows."""
    player_hollows = sum(board[player])
    other_hollows = sum(board[next_player[player]])
    return score(board, player) + player_hollows - other_hollows


def is_game_over(board, player):
    """The game is over if all hollows on the current player's side are empty."""
    return all(x == 0 for x in board[player])


def max_min_move(board, player, depth, max_for_player):
    """
    Recursively compute the minimax move.
    
    Returns a tuple: (move, score)
    """
    if depth == -1 or is_game_over(board, player):
        return None, final_score(board, max_for_player)

    moves = get_moves(board, player)
    maximise = (max_for_player == player)
    worst_score = float("-inf") if maximise else float("inf")
    best_move = (moves[0], worst_score)

    for move in moves:
        new_board, new_player = update_board(board, move, player)
        _, sc = max_min_move(new_board, new_player, depth - 1, max_for_player)
        if maximise and sc >= best_move[1]:
            best_move = (move, sc)
        elif not maximise and sc <= best_move[1]:
            best_move = (move, sc)
    return best_move


def get_ai_move(board, player):
    return max_min_move(board, player, ai_move_depth, player)[0]


def game():
    """Main game loop."""
    player = 'one'
    game_board = copy_board(initial_board)
    print_board(game_board)

    while not is_game_over(game_board, player):
        print(f"\nIt's player {player}'s turn")
        if player == 'one':
            try:
                move_input = input("Move (0-5): ")
                move = int(move_input)
            except ValueError:
                print("Invalid input. Try again.")
                continue
        else:
            move = get_ai_move(game_board, player)
            print("AI move:", move)

        new_board, new_player = update_board(game_board, move, player)
        game_board = new_board
        player = new_player
        print_board(game_board)

    print("\nGame over!")
    print("Player one: ", game_board['onePot'] + sum(game_board['one']))
    print("Player two: ", game_board['twoPot'] + sum(game_board['two']))
    sys.exit()


def test_simple_moves():
    board1 = copy_board(initial_board)
    assert board_eq(board1, initial_board)

    board2, _ = update_board(board1, 0, 'one')
    expected_board2 = {
        'one': [0, 4, 4, 4, 3, 3],
        'two': [3, 3, 3, 3, 3, 3],
        'onePot': 0,
        'twoPot': 0
    }
    assert board_eq(board2, expected_board2)

    board3, _ = update_board(board2, 4, 'one')
    expected_board3 = {
        'one': [0, 4, 4, 4, 0, 4],
        'two': [4, 3, 3, 3, 3, 3],
        'onePot': 1,
        'twoPot': 0
    }
    assert board_eq(board3, expected_board3)

    board4, _ = update_board(board3, 5, 'two')
    expected_board4 = {
        'one': [1, 5, 4, 4, 0, 4],
        'two': [4, 3, 3, 3, 3, 0],
        'onePot': 1,
        'twoPot': 1
    }
    assert board_eq(board4, expected_board4)

    board5, _ = update_board(board4, 0, 'two')
    expected_board5 = {
        'one': [1, 5, 4, 4, 0, 4],
        'two': [0, 4, 4, 4, 4, 0],
        'onePot': 1,
        'twoPot': 1
    }
    assert board_eq(board5, expected_board5)

    board6, _ = update_board(board5, 1, 'two')
    expected_board6 = {
        'one': [0, 5, 4, 4, 0, 4],
        'two': [0, 0, 5, 5, 5, 0],
        'onePot': 1,
        'twoPot': 3
    }
    assert board_eq(board6, expected_board6)
    print("test_simple_moves passed")


def test_final_score():
    board = {
        'onePot': 1,
        'twoPot': 2,
        'one': [0, 0, 10, 11, 0, 0],
        'two': [6, 5, 0, 0, 0, 0]
    }
    assert final_score(board, 'one') == 9
    # 13 - 22 equals -9.
    assert final_score(board, 'two') == (13 - 22)
    print("test_final_score passed")


def tests():
    test_simple_moves()
    test_final_score()

    mm_board1 = copy_board(initial_board)
    move, sc = max_min_move(mm_board1, 'one', 0, 'one')
    assert move == 3
    assert sc == 0

    move, sc = max_min_move(mm_board1, 'one', 2, 'one')
    assert move == 3
    assert sc == 6

    print("tests passed")
    sys.exit()


if __name__ == '__main__':
    # To run tests instead of playing a game, uncomment the following line:
    # tests()
    game()
