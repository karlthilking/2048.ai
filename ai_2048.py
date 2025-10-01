from jedi.parser_utils import cut_value_at_position

from game_2048 import *
import numpy as np

game = Game2048GUI()

def get_empty_cells(board):
    empty_cells = []
    for i in range(4):
        for j in range(4):
            if board[i, j] == 0:
                empty_cells.append([i, j])

    return empty_cells

def place_cell(board, coords, val):
    new_board = board.copy()
    new_board[coords] = val
    return new_board

# ordered tiles indicate better game state
def monotonic_rating(board):
    # horizontal monotonicity
    for i in range(4):
        cur, next = 0, 1
        while next < 4:
            while next < 4 and board[i, next] == 0:
                next += 1
            if next >= 4:
                next -= 1
                break

            cur_val = board[i, cur]
            next_val = board[i, next]

            if cur_val > next_val:

            elif next_val > cur_val:


    # vertical monotonicity
    for j in range(4):


# better game state when adjacent tiles have similar values
def smoothness_rating(board):
    rating = 0

    for i in range(4):
        for j in range(4):
            if board[i, j] != 0:
                val = np.log2(board[i, j])
                if j < 3 and board[i, j + 1] != 0:
                    right_val = np.log2(board[i, j + 1])
                    rating -= abs(val - right_val)
                if i < 3 and board[i + 1, j] != 0:
                    down_val = np.log2(board[i, j + 1])
                    rating -= abs(val - down_val)

    return rating

# corner position most desirable, edge position next best
def max_tile_position_rating(board):
    corner_tiles = [board[0,0], board[0, 3], board[3, 0], board[3, 3]]
    max_val, max_position = get_max_tile(board)

    if max_val in corner_tiles:
        return max_val * 2

    max_edge_tiles = [np.max(board[0, :]), np.max(board[:, 0]), np.max(board[3, :]), np.max(board[:, 3])]
    if max_val in max_edge_tiles:
        return max_val * 0.5

    return 0

def get_max_tile(board):
    return np.max(board), np.argmax(board)

def is_game_over(board):
    if np.any(board == 0):
        return False

    for i in range(4):
        for j in range(4):
            cell = board[i, j]
            if j < 3 and cell == board[i, j + 1]:
                return False
            if i < 3 and cell == board[i + 1, j]:
                return False

    return True

def evaluate(board):
    if is_game_over(board):
        return -float('inf')

    return (
        (len(get_empty_cells(board)) * 10000) +
        (monotonic_rating(board) * 50) +
        (smoothness_rating(board) * 10) +
        (max_tile_position_rating(board) * 1000) +
        (get_max_tile(board)[0] * 10)
    )

def execute_move(board, move):
    if move == 0:
        return execute_up(board)
    elif move == 1:
        return execute_down(board)
    elif move == 2:
        return execute_left(board)
    else:
        return execute_right(board)

def execute_left(board):
    new_board = board.copy()

    for i in range(4):
        row = new_board[i, :]
        non_zero = row[row != 0]

        new_row, j = [], 0
        while j < len(non_zero):
            if j < len(non_zero) - 1 and non_zero[j] == non_zero[j + 1]:
                new_val = non_zero[j] * 2
                new_row.append(new_val)
                j += 2
            else:
                new_row.append(non_zero[j])
                j += 1
        while len(new_row) < 4:
            new_row.append(0)

        new_board[i, :] = new_row

    return new_board

def execute_right(board):
    flipped_board = np.fliplr(board)
    new_board = execute_left(flipped_board)
    return np.fliplr(new_board)

def execute_up(board):
    transposed_board = board.T
    new_board = execute_left(transposed_board)
    return new_board.T

def execute_down(board):
    transposed_board = board.T
    new_board = execute_right(transposed_board)
    return new_board.T

def expectimax(board, depth, choose_move):
    if depth == 0 or game.is_game_over():
        return evaluate(board)
    if choose_move:
        max_val = -float('inf')
        for move in game.actions:
            new_board, changed = execute_move(board, move)
            if changed:
                val = expectimax(new_board, depth - 1, False)
                max_val = max(val, max_val)
        return max_val

    else:
        expected_value = 0
        empty_cells = get_empty_cells(board)

        for empty_cell in empty_cells:
            rand = random.random()
            if rand < 0.9:
                new_board_2 = place_cell(board, empty_cell, 2)
                probability_2 = 0.9 * (1.0 / len(empty_cells))
                expected_value += probability_2 * expectimax(new_board_2, depth - 1, True)
            else:
                new_board_4 = place_cell(board, empty_cell, 4)
                probability_4 =  0.1 * (1.0 / len(empty_cells))
                expected_value += probability_4 * expectimax(new_board_4, depth - 1, True)

        return expected_value







