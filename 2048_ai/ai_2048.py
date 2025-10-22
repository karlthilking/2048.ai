from game_2048 import *
import numpy as np
import json
import sys

class AI2048:
    def __init__(self, config):
        self.weight_matrix = np.array([
            [65536, 32768, 16384, 8192],
            [512, 1024, 2048, 4096],
            [256, 128, 64, 32],
            [2, 4, 8, 16]
        ])
        self.game = None
        self.algo = config['algorithm']
        self.depth = config['depth']
        self.var_depth = config['variable_depth']
        self.max_depth = config['max_depth']
        self.min_depth = config['min_depth']
        self.save_results = config['save_results']
        self.output_file = config['output_file']
        self.num_games = config['num_games']

    def get_empty_tiles(self, board):
        empty_tiles = []
        for i in range(4):
            for j in range(4):
                if board[i, j] == 0:
                    empty_tiles.append([i, j])
        return empty_tiles

    def game_over(self, board):
        for i in range(4):
            for j in range(4):
                if board[i, j] == 0:
                    return False
                elif i < 3 and board[i, j] == board[i + 1, j]:
                    return False
                elif j < 3 and board[i, j] == board[i, j + 1]:
                    return False
        return True

    def get_actions(self, board):
        all_actions = ['up', 'down', 'left', 'right']
        actions = []
        for action in all_actions:
            temp = self.execute_action(action, board)
            if not np.array_equal(temp, board):
                actions.append(action)
        return actions

    def execute_action(self, action, board):
        match action:
            case 'left':
                return self.execute_left(board)
            case 'right':
                return self.execute_right(board)
            case 'up':
                return self.execute_up(board)
            case 'down':
                return self.execute_down(board)
            case _:
                return None

    def execute_left(self, board):
        new_board = board.copy()
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

    def execute_right(self, board):
        new_board = board.copy()
        new_board = np.fliplr(new_board)
        new_board = self.execute_left(new_board)
        return np.fliplr(new_board)

    def execute_up(self, board):
        new_board = board.copy()
        new_board = new_board.T
        new_board = self.execute_left(new_board)
        return new_board.T

    def execute_down(self, board):
        new_board = board.copy()
        new_board = new_board.T
        new_board = self.execute_right(new_board)
        return new_board.T

    def place_tile(self, board, tile, value):
        new_board = board.copy()
        new_board[tile] = value
        return new_board

    def evaluate_board(self, board):
        if self.game_over(board):
            return -float('inf')
        formation = self.formation_score(board)
        return formation

    def formation_score(self, board):
        return np.sum(np.multiply(board, self.weight_matrix))

    def empty_score(self, board):
        return len(self.get_empty_tiles(board))

    def get_best_action(self, board, algorithm, depth):
        match algorithm:
            case "expectimax":
                return self.expectimax(board, depth, True)[1]
            case "minimax":
                return self.minimax(board, depth, True)[1]
            case "alphabeta":
                return self.alphabeta(board, depth, True, -float('inf'), float('inf'))[1]
            case _:
                return None

    def expectimax(self, board, depth, max_node):
        if depth == 0 or self.game_over(board):
            return self.evaluate_board(board), None
        if max_node:
            actions = self.get_actions(board)
            max_value, max_action = -float('inf'), None
            for action in actions:
                new_board = self.execute_action(action, board)
                value = self.expectimax(new_board, depth - 1, False)[0]
                if value > max_value:
                    max_value, max_action = value, action
            return max_value, max_action
        else:
            empty_tiles = self.get_empty_tiles(board)
            expected_value = 0
            for tile in empty_tiles:
                board_2 = self.place_tile(board, tile, 2)
                board_4 = self.place_tile(board, tile, 4)
                value_2 = self.expectimax(board_2, depth - 1, True)[0]
                value_4 = self.expectimax(board_4, depth - 1, True)[0]
                probability_2 = (0.9 / len(empty_tiles))
                probability_4 = (0.1 / len(empty_tiles))
                expected_value += ((value_2 * probability_2) + (value_4 * probability_4))
            return expected_value, None

    def minimax(self, board, depth, max_node):
        if depth == 0 or self.game_over(board):
            return self.evaluate_board(board), None
        if max_node:
            actions = self.get_actions(board)
            max_value, max_action = -float('inf'), None
            for action in actions:
                new_board = self.execute_action(action, board)
                value = self.minimax(new_board, depth - 1, False)[0]
                if value > max_value:
                    max_value, max_action = value, action
            return max_value, max_action
        else:
            empty_tiles = self.get_empty_tiles(board)
            min_value = float('inf')
            for tile in empty_tiles:
                board_2 = self.place_tile(board, tile, 2)
                value_2 = self.minimax(board_2, depth - 1, True)[0]
                board_4 = self.place_tile(board, tile, 4)
                value_4 = self.minimax(board_4, depth - 1, True)[0]
                min_value = min(min_value, value_2, value_4)
            return min_value, None

    def alphabeta(self, board, depth, max_node, alpha, beta):
        if depth == 0 or self.game_over(board):
            return self.evaluate_board(board), None
        if max_node:
            actions = self.get_actions(board)
            max_action = None
            for action in actions:
                new_board = self.execute_action(action, board)
                value = self.alphabeta(new_board, depth - 1, False, alpha, beta)
                if value > alpha:
                    alpha = value
                    max_action = action
                if alpha > beta:
                    return None, None
            return alpha, max_action
        else:
            empty_tiles = self.get_empty_tiles(board)
            for tile in empty_tiles:
                board_2 = self.place_tile(board, tile, 2)
                value_2 = self.alphabeta(board_2, depth - 1, True, alpha, beta)
                board_4 = self.place_tile(board, tile, 4)
                value_4 = self.alphabeta(board_4, depth - 1, True, alpha, beta)
                beta = min(beta, value_2, value_4)
                if alpha > beta:
                    return None, None
            return beta, None

    def play(self, algorithm_choice, depth_choice):
        pygame.init()
        clock = pygame.time.Clock()
        while not self.game.is_game_over():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            current_board = self.game.get_board()
            best_action = self.get_best_action(current_board, algorithm_choice, depth_choice)
            if best_action:
                self.game.handle_move(best_action)
                self.game.draw()
                clock.tick(2)
            else:
                break
        pygame.quit()
        return self.game.score, np.max(self.game.board)

    def run(self):
        results = {}
        for i in range(self.num_games):
            self.game = Game2048()
            score, max_tile = self.play(self.algo, self.depth)
            results[i] = (score, max_tile)
        if self.save_results:
            with open(self.output_file, 'w') as f:
                json.dump(results, f)
