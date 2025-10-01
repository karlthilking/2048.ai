import pygame
import numpy as np
import random
import sys

class Game2048GUI:
    def __init__(self, width=600, height=700):
        pygame.init()

        self.width = width
        self.height = height
        self.grid_size = 4
        self.cell_size = 120
        self.cell_padding = 10
        self.grid_padding = 50

        self.actions = {
            0: 'up',
            1: 'down',
            2: 'left',
            3: 'right'
        }

        self.grid_width = self.grid_size * self.cell_size + (self.grid_size + 1) * self.cell_padding
        self.grid_height = self.grid_width

        self.colors = {
            0: (205, 193, 180),
            2: (238, 228, 218),
            4: (237, 224, 200),
            8: (242, 177, 121),
            16: (245, 149, 99),
            32: (246, 124, 95),
            64: (246, 94, 59),
            128: (237, 207, 114),
            256: (237, 204, 97),
            512: (237, 200, 80),
            1024: (237, 197, 63),
            2048: (237, 194, 46),
        }
        self.default_color = (60, 58, 50)
        self.background_color = (187, 173, 160)
        self.text_light = (119, 110, 101)
        self.text_dark = (249, 246, 242)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("2048 Game")

        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.board = np.zeros((4, 4), dtype=np.int32)
        self.score = 0
        self.game_over = False
        self.won = False

        self.reset_game()

    def reset_game(self):
        self.board = np.zeros((4, 4), dtype=np.int32)
        self.score = 0
        self.game_over = False
        self.won = False
        self.add_random_tile()
        self.add_random_tile()

    def add_random_tile(self):
        empty_cells = np.argwhere(self.board == 0)
        if len(empty_cells) > 0:
            idx = np.random.choice(len(empty_cells))
            x, y = empty_cells[idx]
            value = 2 if random.random() < 0.9 else 4
            self.board[x, y] = value

    def move_left(self):
        new_board = self.board.copy()
        score_gained = 0

        for i in range(4):
            row = new_board[i, :]
            non_zero = row[row != 0]

            merged_row = []
            j = 0
            while j < len(non_zero):
                if j < len(non_zero) - 1 and non_zero[j] == non_zero[j + 1]:
                    merged_value = non_zero[j] * 2
                    merged_row.append(merged_value)
                    score_gained += merged_value
                    j += 2
                else:
                    merged_row.append(non_zero[j])
                    j += 1

            while len(merged_row) < 4:
                merged_row.append(0)

            new_board[i, :] = merged_row

        changed = not np.array_equal(self.board, new_board)
        if changed:
            self.board = new_board
            self.score += score_gained

        return changed

    def move_right(self):
        self.board = np.fliplr(self.board)
        changed = self.move_left()
        self.board = np.fliplr(self.board)
        return changed

    def move_up(self):
        self.board = self.board.T
        changed = self.move_left()
        self.board = self.board.T
        return changed

    def move_down(self):
        self.board = self.board.T
        changed = self.move_right()
        self.board = self.board.T
        return changed

    def is_game_over(self):
        if np.any(self.board == 0):
            return False

        for i in range(4):
            for j in range(4):
                current = self.board[i, j]
                if j < 3 and current == self.board[i, j + 1]:
                    return False
                if i < 3 and current == self.board[i + 1, j]:
                    return False

        return True

    def handle_move(self, direction):
        if self.game_over:
            return

        moved = False
        if direction == 'left':
            moved = self.move_left()
        elif direction == 'right':
            moved = self.move_right()
        elif direction == 'up':
            moved = self.move_up()
        elif direction == 'down':
            moved = self.move_down()

        if moved:
            self.add_random_tile()

            if not self.won and np.any(self.board >= 2048):
                self.won = True

            if self.is_game_over():
                self.game_over = True

    def draw_cell(self, x, y, value):
        cell_x = self.grid_padding + x * (self.cell_size + self.cell_padding)
        cell_y = 120 + self.grid_padding + y * (self.cell_size + self.cell_padding)

        color = self.colors.get(value, self.default_color)

        pygame.draw.rect(self.screen, color,
                         (cell_x, cell_y, self.cell_size, self.cell_size),
                         border_radius=6)

        if value != 0:
            text_color = self.text_light if value <= 4 else self.text_dark

            if value < 100:
                font = self.font_large
            elif value < 1000:
                font = self.font_medium
            else:
                font = self.font_small

            text = font.render(str(value), True, text_color)
            text_rect = text.get_rect(center=(cell_x + self.cell_size // 2,
                                              cell_y + self.cell_size // 2))
            self.screen.blit(text, text_rect)

    def draw(self):
        self.screen.fill((250, 248, 239))

        title = self.font_large.render("2048", True, (119, 110, 101))
        self.screen.blit(title, (50, 30))

        score_text = self.font_medium.render(f"Score: {self.score}", True, (119, 110, 101))
        self.screen.blit(score_text, (300, 40))

        grid_bg = pygame.Rect(self.grid_padding - 10, 120 + self.grid_padding - 10,
                              self.grid_width + 20, self.grid_height + 20)
        pygame.draw.rect(self.screen, self.background_color, grid_bg, border_radius=6)

        for i in range(4):
            for j in range(4):
                self.draw_cell(j, i, self.board[i, j])

        if self.won and not self.game_over:
            msg = self.font_large.render("You Won! Keep playing?", True, (119, 110, 101))
            msg_rect = msg.get_rect(center=(self.width // 2, 600))
            self.screen.blit(msg, msg_rect)

        if self.game_over:
            msg = self.font_large.render("Game Over! Press R to restart", True, (119, 110, 101))
            msg_rect = msg.get_rect(center=(self.width // 2, 600))
            self.screen.blit(msg, msg_rect)

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_r, pygame.K_SPACE]:
                        self.reset_game()
                    elif not self.game_over:
                        if event.key in [pygame.K_LEFT, pygame.K_a]:
                            self.handle_move('left')
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            self.handle_move('right')
                        elif event.key in [pygame.K_UP, pygame.K_w]:
                            self.handle_move('up')
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            self.handle_move('down')

            self.draw()
            clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game2048GUI()
    game.run()


