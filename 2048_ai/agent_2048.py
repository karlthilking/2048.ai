from game_2048 import *
import numpy as np
import json
import sys

class AI2048:
    def __init__(self, game):
        self.game = game

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
        if self.is_game_over(board):
            return -float('inf')
        position_score = self.calculate_position_score(board)
        empty_score = self.calculate_empty_score(board)
        max_tile_score = np.max(board) * 500
        print(f"Position score: {position_score}, Empty score: {empty_score}")
        return position_score + empty_score + max_tile_score

    def calculate_empty_score(self, board):
        empty_count = len(self.get_empty_cells(board))
        return (empty_count ** 2) * np.sum(board) * 10000

    def calculate_position_score(self, board):
        weight_matrix = np.array([
            [4**15, 4**14, 4**13, 4**12],
            [4**8, 4**9, 4**10, 4**11],
            [4**7, 4**6, 4**5, 4**4],
            [1, 4, 4**2, 4**3]
        ])
        score = 0
        for i in range(4):
            for j in range(4):
                score += board[i, j] * weight_matrix[i, j]
        return score

    def calculate_gradient_score(self, board):
        max_val = np.max(board)
        max_pos = np.unravel_index(np.argmax(board), board.shape)
        if max_pos != (0, 0):
            return -1000
        score = 0
        for i in range(3):
            if board[0, i] >= board[0, i + 1] and board[0, i + 1] > 0:
                score += board[0, i + 1]
            if board[i, 0] >= board[i + 1, 0] and board[i + 1, 0] > 0:
                score += board[i + 1, 0]
        return score * 2

    def calculate_merge_score(self, board):
        merges = 0
        for i in range(4):
            for j in range(3):
                if board[i, j] != 0 and board[i, j] == board[i, j + 1]:
                    merges += 1
        for i in range(3):
            for j in range(4):
                if board[i, j] != 0 and board[i, j] == board[i + 1, j]:
                    merges += 1
        return merges * 25000

    def get_best_move(self, board):
        _, best_move = self.expectimax(board, 5, True)
        return best_move

    def expectimax(self, board, depth, is_player_turn):
        if depth == 0 or self.is_game_over(board):
            return self.evaluate_board(board), None
        if is_player_turn:
            valid_moves = self.get_valid_moves(board)
            best_value, best_move = -float('inf'), None
            for move in valid_moves:
                new_board = self.simulate_move(move, board)
                result = self.expectimax(new_board, depth -1, False)
                value = result[0] if isinstance(result, tuple) else result
                if value > best_value:
                    best_value, best_move = value, move
            return best_value, best_move
        else:
            empty_cells = self.get_empty_cells(board)
            expected_value = 0
            for cell in empty_cells:
                new_board_2 = self.place_tile(board, cell, 2)
                new_board_4 = self.place_tile(board, cell, 4)
                probability_2 = (0.9 / len(empty_cells))
                probability_4 = (0.1 / len(empty_cells))
                result_2 = self.expectimax(new_board_2, depth - 1, True)
                result_4 = self.expectimax(new_board_4, depth - 1, True)
                value_2 = result_2[0] if isinstance(result_2, tuple) else result_2
                value_4 = result_4[0] if isinstance(result_4, tuple) else result_4
                expected_value += ((probability_2 * value_2) + (probability_4 * value_4))
            return expected_value

    def solve(self):
        pygame.init()
        clock = pygame.time.Clock()
        while not self.game.is_game_over():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            current_board = self.game.get_board()
            best_move = self.get_best_move(current_board)
            if best_move:
                self.game.handle_move(best_move)
                self.game.draw()
                clock.tick(2)
            else:
                break
        pygame.quit()
        return self.game.score, np.max(self.game.board)

if __name__ == "__main__":
    print("Enter the number of games you want to run: ")
    games = int(input())
    results = {}
    for i in range(games):
        game = Game2048()
        agent = AI2048(game)
        score, max_tile = agent.solve()
        print(f"Score: {score}, Max tile: {max_tile}")
        results[i] = [score, max_tile]