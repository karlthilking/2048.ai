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
            self.calculate_smoothness(board) +
            self.calculate_monotonicity(board) +
            self.calculate_corner_preference(board) +
            self.calculate_available_merges(board) +
            self.get_max_tile(board)
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
        corner_positions = [[0, 0], [0, 3], [3, 0], [3, 3]]
        for corner in corner_positions:
            row = corner[0], col = corner[1]
            if board[row, col] == max_tile:
                return 1000
        edges = [board[0, :], board[3, :], board[:, 0], board[:, 3]]
        for edge in edges:
            if max_tile in edge:
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
        best_move = None
        best_value = 0
        valid_moves = self.get_valid_moves(board)
        for move in valid_moves:
            result_board = self.simulate_move(move, board)
            new_value = self.evaluate_board(result_board)
            if new_value > best_value:
                best_move, best_value = move, new_value
        return best_move

    def expectimax(self, board, depth, is_player_turn):
        if depth == 0 or self.is_game_over(board):
            return self.evaluate_board(board)
        if is_player_turn:
            best_move = self.get_best_move(board)
            new_board = self.simulate_move(best_move, board)
            best_value = self.expectimax(new_board, depth - 1, False)
            return best_value
        else:
            expected_value = 0
            empty_cells = self.get_empty_cells(board)
            for cell in empty_cells:
                result_board_2 = self.place_tile(board, cell, 2)
                result_board_4 = self.place_tile(board, cell, 4)
                value_2 = self.expectimax(result_board_2, depth - 1, True)
                value_4 = self.expectimax(result_board_4, depth - 1, True)
                expected_value += ((value_2 * 0.9 / len(empty_cells)) + (value_4 * 0.1 / len(empty_cells)))
            return expected_value

if __name__ == "__main__":








