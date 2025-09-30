import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Optional, Tuple, Any, Dict
import random

from gymnasium.core import RenderFrame


class Game2048(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, render_mode: Optional[str]=None):

        self.size = 4
        self.goal_state = 2048

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low = 0, high = 2**17, shape=(self.size, self.size), dtype=np.int32)

        self.render_mode = render_mode

        self.board = None
        self.score = 0
        self.game_end = False

    def reset(self, seed: Optional[int]=None, options: Optional[Dict]=None) -> Tuple[np.ndarray, Dict]:
        super().reset(seed=seed)

        self.board = np.zeros((self.size, self.size), dtype=np.int32)
        self.score = 0
        self.game_end = False

        self._add_random_tile()
        self._add_random_tile()

        return self.board.copy(), {}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        if self.game_end:
            return self.board.copy(), 0, True, False, {}

        prev_board = self.board.copy()
        prev_score = self.score

        moved = self._move(action)

        reward = self.score - prev_score

        if moved:
            self._add_random_tile()
            self.game_end = self._is_game_end()
        else:
            reward -= 1

        terminated = self.game_end

        game_win = np.any(self.board >= self.goal_state)
        if game_win:
            reward += 1000

        info = {
            "score": self.score,
            "moved": moved,
            "won": game_win,
            "highest_tile": np.max(self.board)
        }

        return self.board.copy(), reward, terminated, False, info

    def _move(self, action: int) -> bool:
        prev_board, score_increase = self.board.copy(), 0

        # up
        if action == 0:
            self.board, score_increase = self._move_up(self.board)
        # down
        if action == 1:
            self.board, score_increase = self._move_down(self.board)
        # left
        if action == 2:
            self.board, score_increase = self._move_left(self.board)
        # right
        if action == 3:
            self.board, score_increase = self._move_right(self.board)

        self.score += score_increase

        return not np.array_equal(prev_board, self.board)

    def _move_left(self, board: np.ndarray) -> Tuple[np.ndarray, int]:
        new_board, score_increase = board.copy(), 0

        for i in range(self.size):
            row = new_board[i, :]
            elements = row[row != 0]

            updated_row, j = [], 0
            while j < len(elements):
                if j < len(elements) - 1 and elements[j] == elements[j + 1]:
                    updated_cell = elements[j] * 2
                    updated_row.append(updated_cell)
                    score_increase += updated_cell
                    j += 2
                else:
                    updated_row.append(elements[j])
                    j += 1
            while len(updated_row) < self.size:
                updated_row.append(0)
            new_board[i, :] = updated_row

        return new_board, score_increase

    def _move_right(self, board: np.ndarray) -> Tuple[np.ndarray, int]:
        flipped_board = np.fliplr(board)
        new_flipped_board, score_increase = self._move_left(flipped_board)
        return np.fliplr(new_flipped_board), score_increase

    def _move_up(self, board: np.ndarray) -> Tuple[np.ndarray, int]:
        transposed_board = board.T
        new_board, score_increase = self._move_left(transposed_board)
        return new_board.T, score_increase


    def _move_down(self, board: np.ndarray) -> Tuple[np.ndarray, int]:
        transposed_board = board.T
        new_board, score_increase = self._move_right(transposed_board)
        return new_board.T, score_increase

    def _add_random_tile(self):
        empty_cells = np.argwhere(self.board == 0)

        if len(empty_cells) > 0:
            ix = np.random.choice(len(empty_cells))
            x, y = empty_cells[ix]
            cell_val = 2 if random.random() < 0.9 else 4
            self.board[x, y] = cell_val

    def _is_game_end(self) -> bool:
        if np.any(self.board == 0):
            return False

        for action in range(4):
            test_board = self.board.copy()

            if action == 0:
                updated_test_board, _ = self._move_up(test_board)
            elif action == 1:
                updated_test_board, _ = self._move_down(test_board)
            elif action == 2:
                updated_test_board, _ = self._move_left(test_board)
            else:
                updated_test_board, _ = self._move_right(test_board)

            if not np.array_equal(test_board, updated_test_board):
                return False

        return True


    def render(self, mode: str="human"):
        if mode == "human":
            print(f"\nScore: {self.score}")
            print("\n")

            for r in range(self.size):
                for c in range(self.size):
                    print("   ", end="")
                    if self.board[r, c] == 0:
                        print("   ", end=" |")
                    else:
                        print(f"{self.board[r, c]:4d}", end=" |")
                print()
            print("\n")

        elif mode == "rgb_array":

            colors = {
                0: '#',
                2: '#',
                4: '#',
                8: '#',
                16: '#',
                32: '#',
                64: '#',
                128: '#',
                256: '#',
                512: '#',
                1024: '#',
                2048: '#'
            }


    def get_valid_actions(self) -> list:
        cur_valid_actions = []
        test_board = self.board.copy()

        for action in range(4):
            if action == 0:
                updated_test_board, _ = self._move_up(test_board)
            elif action == 1:
                updated_test_board, _ = self._move_down(test_board)
            elif action == 2:
                updated_test_board, _ = self._move_left(test_board)
            else:
                updated_test_board, _ = self._move_right(test_board)

            if not np.array_equal(updated_test_board, test_board):
                cur_valid_actions.append(action)

        return cur_valid_actions


if __name__ == "__main__":
    env = Game2048()

    obs, info = env.reset()
    env.render()

    # test game
    for step in range(10000):
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            break

        action = random.choice(valid_actions)
        action_name = ["up", "down", "left", "right"]

        obs, reward, terminated, truncated, info = env.step(action)
        env.render()

        if terminated:
            print("Game Over")

    print("Completed testing")











