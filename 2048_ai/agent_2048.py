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
        empty_cells = len(self.get_empty_cells(board))
        monotonicity = self.calculate_monotonic_score(board)
        corner_score = self.max_tile_position(board)
        gradient_score = self.calculate_gradient_bonus(board)
        merge_potential = self.calculate_merge_potential(board)
        max_tile_value = np.max(board)
        return (
            empty_cells * 300 +
            monotonicity * 5 +
            corner_score * 2+
            gradient_score * 500 +
            merge_potential * 50 +
            max_tile_value * 2
        )

    def calculate_monotonic_score(self, board):
        score = 0
        for i in range(4):
            row = board[i, :][board[i, :] != 0]
            if len(row) > 1:
                increasing = all([row[j] <= row[j + 1] for j in range(len(row) - 1)])
                decreasing = all([row[j] >= row[j + 1] for j in range(len(row) - 1)])
                if increasing or decreasing:
                    score += (len(row) ** 2) * 50
        for j in range(4):
            col = board[:, j][board[:, j] != 0]
            if len(col) > 1:
                increasing = all([col[i] <= col[i + 1] for i in range(len(col) - 1)])
                decreasing = all([col[i] >= col[i + 1] for i in range(len(col) - 1)])
                if increasing or decreasing:
                    score += (len(col) ** 2) * 50
        return score

    def max_tile_position(self, board):
        max_tile_positions = np.argwhere(board == np.max(board))
        best_score = 0
        for pos in max_tile_positions:
            row, col = pos[0], pos[1]
            if (row, col) in [(0, 0), (0, 3), (3, 0), (3, 3)]:
                return 1000
            elif row == 0 or row == 3 or col == 0 or col == 3:
                best_score = max(best_score, 200)
            else:
                best_score = max(best_score, -400)
        return best_score

    def calculate_gradient_bonus(self, board):
        max_tile = np.max(board)
        score = 0
        corners = [(0, 0), (0, 3), (3, 0), (3, 3)]
        for row, col in corners:
            directions = []
            if row == 0 and col == 0:
                directions = [(0, 1), (1, 0)]
            elif row == 0 and col == 3:
                directions = [(1, 0), (0, -1)]
            elif row == 3 and col == 0:
                directions = [(-1, 0), (0, 1)]
            else:
                directions = [(-1, 0), (0, -1)]
            for dr, dc in directions:
                r, c = row + dr, col + dc
                if 0 <= r < 4 and 0 <= c < 4 and board[r, c] != 0:
                    if board[r, c] <= board[row, col]:
                        score += np.log2(board[r, c])
                break
        return score
    def calculate_merge_potential(self, board):
        merge_score = 0
        for i in range(4):
            for j in range(3):
                if board[i, j] != 0 and board[i, j] == board[i, j + 1]:
                    merge_score += board[i, j]
        for i in range(3):
            for j in range(4):
                if board[i, j] != 0 and board[i, j] == board[i + 1, j]:
                    merge_score += board[i, j]
        return merge_score

    # add later
    # def calculate_snake_pattern(self, board):

    def get_best_move(self, board):
        max_tile = np.max(board)
        num_empty_cells = len(self.get_empty_cells(board))
        if max_tile >= 1024:
            depth = 6
        elif max_tile >= 512:
            depth = 5
        elif max_tile >= 256:
            depth = 4
        elif num_empty_cells <= 4:
            depth = 5
        else:
            depth = 3
        _, best_move = self.expectimax(board, depth, True)
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
    for i in range(games):
        game = Game2048()
        agent = AI2048(game)
        score, max_tile = agent.solve()
        print(f"Score: {score}, Best tile: {max_tile}")
