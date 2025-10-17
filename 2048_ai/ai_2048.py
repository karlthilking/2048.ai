from time import monotonic

from game_2048 import *

import numpy as np
import random

class AI20248:
    def __init__(self, game):
        self.game = game
        self.board = game.board

    def get_empty_cells(self, board):
        empty_cells = []
        for i in range(4):
            for j in range(4):
                if board[i, j] == 0:
                    empty_cells.append([i, j])
        return empty_cells

    def is_game_over(self, board):
        for i in range(4):
            for j in range(4):
                if board[i, j] == 0:
                    return False
                elif i < 3 and board[i, j] == board[i + 1, j]:
                    return False
                elif j < 3 and board[i, j] == board[i, j + 1]:
                    return False
        return True

    def copy_board(self, board):
        return board.copy()

    def board_equals(self, board1, board2):
        return np.array_equal(board1, board2)

    def get_valid_moves(self, board):
        all_moves = ['left', 'right', 'up', 'down']
        valid_moves = []
        for move in all_moves:
            temp_board = self.simulate_move(move, board)
            if not self.board_equals(temp_board, board):
                valid_moves.append(move)
        return valid_moves

    def get_max_tile(self, board):
        return np.max(board)

    def simulate_move(self, move, board):
        match move:
            case 'left':
                return self.simulate_left_move(board)
            case 'right':
                return self.simulate_right_move(board)
            case 'up':
                return self.simulate_up_move(board)
            case 'down':
                return self.simulate_down_move(board)
            case _:
                return None

    def simulate_left_move(self, board):
        new_board = self.copy_board(board)
        for i in range(4):
            row = new_board[i, :]
            non_zero = row[row != 0]
            new_row, j = [], 0
            while j < len(non_zero):
                if j < len(non_zero) - 1 and non_zero[j] == non_zero[j + 1]:
                    new_row.append(2 * non_zero[j])
                    j += 2
                else:
                    new_row.append(non_zero[j])
                    j += 1
            while len(new_row) < 4:
                new_row.append(0)
            new_board[i, :] = new_row
        return new_board

    def simulate_right_move(self, board):
        new_board = self.copy_board(board)
        new_board = np.fliplr(new_board)
        new_board = self.simulate_left_move(new_board)
        return np.fliplr(new_board)

    def simulate_up_move(self, board):
        new_board = self.copy_board(board)
        new_board = new_board.T
        new_board = self.simulate_left_move(new_board)
        return new_board.T

    def simulate_down_move(self, board):
        new_board = self.copy_board(board)
        new_board = new_board.T
        new_board = self.simulate_right_move(new_board)
        return new_board.T

    def place_tile(self, board, position, value):
        new_board = self.copy_board(board)
        new_board[position] = value
        return new_board

    def evaluate_board(self, board):
        return (
            self.calculate_smoothness(board)  * 200 +
            self.calculate_monotonicity(board) * 500 +
            self.calculate_corner_preference(board) +
            self.calculate_available_merges(board) * 200 +
            self.get_max_tile(board) * 2
        )
    def calculate_smoothness(self, board):
        smoothness_score = 0
        for i in range(3):
            for j in range(3):
                if board[i, j] == 0:
                    continue
                if board[i, j] != board[i + 1, j] and board[i + 1, j] != 0:
                    smoothness_score -= abs(np.log2(board[i, j]) - np.log2(board[i + 1, j]))
                if board[i, j] != board[i, j + 1] and board[i, j + 1] != 0:
                    smoothness_score -= abs(np.log2(board[i, j]) - np.log2(board[i, j + 1]))
        return smoothness_score

    def calculate_monotonicity(self, board):
        monotonic_score = 0
        for i in range(4):
            ascending_score = descending_score = 0
            for j in range(3):
                if board[i, j] <= board[i, j + 1]:
                    ascending_score += 1
                if board[i, j] >= board[i, j + 1]:
                    descending_score += 1
            monotonic_score += max(ascending_score, descending_score)

        for j in range(4):
            ascending_score = descending_score = 0
            for i in range(3):
                if board[i, j] <= board[i + 1, j]:
                    ascending_score += 1
                if board[i, j] >= board[i + 1, j]:
                    descending_score += 1
            monotonic_score += max(ascending_score, descending_score)
        return monotonic_score

    def calculate_corner_preference(self, board):
        max_tile = self.get_max_tile(board)
        max_positions = np.argwhere(board == max_tile)
        for pos in max_positions:
            row, col = pos[0], pos[1]
            if (row, col) in [(0, 0), (0, 3), (3, 0), (3, 3)]:
                return 1000
            if row == 0 or row == 3 or col == 0 or col == 3:
                return 250
        return 0

    def calculate_available_merges(self, board):
        available_merges = 0
        for i in range(3):
            for j in range(3):
                if board[i, j] == 0:
                    continue
                if board[i, j] == board[i + 1, j]:
                    available_merges += 1
                if board[i, j] == board[i, j + 1]:
                    available_merges += 1
        return available_merges

    def get_best_move(self, board):
        _, best_move = self.expectimax(board, 4, True)
        return best_move

    def expectimax(self, board, depth, is_player_turn):
        if depth == 0 or self.is_game_over(board):
            return self.evaluate_board(board), None
        if is_player_turn:
            valid_moves = self.get_valid_moves(board)
            best_value, best_move =  -float('inf'), None
            for move in valid_moves:
                new_board = self.simulate_move(move, board)
                value = self.expectimax(new_board, depth - 1, False)
                if value > best_value:
                    best_value, best_move = value, move
            return best_value, best_move
        else:
            empty_cells = self.get_empty_cells(board)
            expected_value = 0
            for cell in empty_cells:
                board_2 = self.place_tile(board, cell, 2)
                board_4 = self.place_tile(board, cell, 4)
                probability_2 = (0.9 / len(empty_cells))
                probability_4 = (0.1 / len(empty_cells))
                result_2 = self.expectimax(board_2, depth - 1, True)
                result_4 = self.expectimax(board_4, depth - 1, True)
                value_2 = result_2[0] if isinstance(result_2, tuple) else result_2
                value_4 = result_4[0] if isinstance(result_4, tuple) else result_4
                expected_value += (probability_2 * value_2) + (probability_4 * value_4)
            return expected_value

    def solve(self):
        self.game.run()
        while not self.game.is_game_over():
            current_board = self.game.get_board()
            best_move = self.get_best_move(current_board)
            if best_move:
                self.game.handle_move(best_move)
            else:
                break


if __name__ == "__main__":
    game = Game2048()
    agent = AI20248(game)
    agent.solve()









