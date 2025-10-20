from game_2048 import *
import numpy as np
import json
import sys

class AI2048:
    def __init__(self, game):
        self.game = game
        self.weight_matrix = np.array([
            [65536, 32768, 16384, 8192],
            [512, 1024, 2048, 4096],
            [256, 128, 64, 32],
            [2, 4, 8, 16]
        ])

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
            print(f"Score: {-float('inf')}")
            return -float('inf')
        empty = self.evaluate_empty_cells(board) * 64 * np.max(board)
        smooth = self.evaluate_smoothness(board) * 40
        snake = self.evaluate_formation(board)
        print(f"Empty: {empty}, Smooth: {smooth}, Snake: {snake}")
        return empty - smooth + snake

    def evaluate_merge_score(self, board):
        score = 0
        for i in range(4):
            for j in range(3):
                if board[i, j] == 0:
                    continue
                if board[i, j] == board[i, j + 1]:
                    score += board[i, j]
        for i in range(3):
            for j in range(4):
                if board[i, j] == 0:
                    continue
                if board[i, j] == board[i + 1, j]:
                    score += board[i, j]
        return score

    def evaluate_formation(self, board):
        return np.sum(np.multiply(board, self.weight_matrix)) / 30

    def evaluate_empty_cells(self, board):
        return len(self.get_empty_cells(board))

    def evaluate_smoothness(self, board):
        penalty = 0
        for i in range(4):
            for j in range(3):
                if board[i, j] == 0:
                    continue
                penalty += abs(board[i, j] - board[i, j + 1])
        for i in range(3):
            for j in range(4):
                if board[i, j] == 0:
                    continue
                penalty += abs(board[i, j] - board[i + 1, j])
        return penalty

    def evaluate_distance(self, board):
        penalty = 0
        constant = 30
        for i in range(4):
            for j in range(4):
                if board[i, j] == 0:
                    continue
                distance = min(i + j, abs(i - 3) + abs(j - 3))
                penalty += board[i, j] * constant * distance
        return penalty

    def get_best_move(self, board):
        if np.max(board) <= 64:
            depth = 4
        else:
            depth = 5
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
                board_2 = self.place_tile(board, cell, 2)
                board_4 = self.place_tile(board, cell, 4)
                result_2 = self.expectimax(board_2, depth - 1, True)
                result_4 = self.expectimax(board_4, depth - 1, True)
                value_2 = result_2[0] if isinstance(result_2, tuple) else result_2
                value_4 = result_4[0] if isinstance(result_4, tuple) else result_4
                expected_value += ((0.9 / len(empty_cells)) * value_2) + ((0.1 / len(empty_cells)) * value_4)
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
    print("Do you want to save your results? (y/n): ")
    save = True if input().split()[0].lower() == 'y' else False
    if save:
        print("Enter current config name: ")
        config_name = input().split()
    results = {}
    for i in range(games):
        game = Game2048()
        agent = AI2048(game)
        score, max_tile = agent.solve()
        print(f"Score: {score}, Max tile: {max_tile}")
        results[i] = f"Score: {score}, Max tile: {max_tile}"
    if save:
        with open(f"{config_name}.json", "w") as f:
            json.dump(results, f, indent=4)