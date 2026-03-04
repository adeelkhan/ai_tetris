import pygame
import random
import math
import array

pygame.init()

BLOCK_SIZE = 18
COLS = 10
ROWS = 20
WIDTH = COLS * BLOCK_SIZE
HEIGHT = ROWS * BLOCK_SIZE
SCREEN_WIDTH = WIDTH + 120
SCREEN_HEIGHT = HEIGHT

BORDER_COLOR = (255, 0, 0)
BG_COLOR = (20, 20, 40)

FALL_SPEED = 500
MOVE_DELAY = 100

COLOR_BLACK = (0, 0, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_BLUE = (0, 0, 255)
COLOR_ORANGE = (255, 165, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_PURPLE = (128, 0, 128)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)

COLORS = [
    COLOR_BLACK,
    COLOR_CYAN,
    COLOR_BLUE,
    COLOR_ORANGE,
    COLOR_YELLOW,
    COLOR_GREEN,
    COLOR_PURPLE,
    COLOR_RED,
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
]


def generate_tone(frequency, duration, volume=0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        value = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
        buf[i] = max(-32768, min(32767, value))
    
    return pygame.mixer.Sound(buffer=buf)


class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.lock_sound = generate_tone(220, 0.1, 0.3)
        self.line_clear_sound = generate_tone(440, 0.15, 0.4)
        self.game_over_sound = generate_tone(150, 0.5, 0.5)

    def play_lock(self):
        self.lock_sound.play()

    def play_line_clear(self):
        self.line_clear_sound.play()

    def play_game_over(self):
        self.game_over_sound.play()


class Tetris:
    def __init__(self, sound_manager=None):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.piece_queue = [random.randint(0, len(SHAPES) - 1) for _ in range(2)]
        self.new_piece()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.sound_manager = sound_manager

    def new_piece(self):
        self.piece_type = self.piece_queue.pop(0)
        self.piece_queue.append(random.randint(0, len(SHAPES) - 1))
        self.piece = [row[:] for row in SHAPES[self.piece_type]]
        self.color = self.piece_type + 1
        self.x = 0
        self.y = 0

    def get_next_piece(self):
        return self.piece_queue[0]

    def rotate(self):
        rotated = [list(row) for row in zip(*reversed(self.piece))]
        if not self.collision(rotated, self.x, self.y):
            self.piece = rotated

    def collision(self, piece, x, y):
        for i in range(len(piece)):
            for j in range(len(piece[i])):
                if piece[i][j]:
                    new_x = x + j
                    new_y = y + i
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                        return True
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return True
        return False

    def lock_piece(self):
        for i in range(len(self.piece)):
            for j in range(len(self.piece[i])):
                if self.piece[i][j]:
                    board_y = self.y + i
                    board_x = self.x + j
                    if board_y >= 0:
                        self.board[board_y][board_x] = self.color
        if self.sound_manager:
            self.sound_manager.play_lock()
        self.clear_lines()
        self.new_piece()
        if self.collision(self.piece, self.x, self.y):
            self.game_over = True
            if self.sound_manager:
                self.sound_manager.play_game_over()

    def clear_lines(self):
        lines_cleared = 0
        for i in range(ROWS):
            if all(self.board[i]):
                self.board.pop(i)
                self.board.insert(0, [0] * COLS)
                lines_cleared += 1
        if lines_cleared > 0 and self.sound_manager:
            self.sound_manager.play_line_clear()
        self.score += lines_cleared * 100

    def move(self, dx, dy):
        if not self.collision(self.piece, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        elif dy > 0:
            self.lock_piece()
        return False

    def draw_block(self, screen, color_idx, x, y, size=BLOCK_SIZE):
        pygame.draw.rect(screen, COLORS[color_idx],
                        (x * size, y * size, size - 1, size - 1))

    def draw_board(self, screen):
        for i in range(ROWS):
            for j in range(COLS):
                if self.board[i][j]:
                    self.draw_block(screen, self.board[i][j], j, i)

    def draw_current_piece(self, screen):
        for i in range(len(self.piece)):
            for j in range(len(self.piece[i])):
                if self.piece[i][j]:
                    self.draw_block(screen, self.color, self.x + j, self.y + i)

    def draw_score_box(self, screen, font):
        score_text = font.render(f"Score: {self.score}", True, COLOR_WHITE)
        pygame.draw.rect(screen, BORDER_COLOR, (WIDTH + 10, 10, 100, 35), 2)
        screen.blit(score_text, (WIDTH + 15, 15))

    def draw_next_piece_box(self, screen, font):
        next_font = font.render("Next", True, COLOR_WHITE)
        pygame.draw.rect(screen, BORDER_COLOR, (WIDTH + 10, 55, 100, 70), 2)
        screen.blit(next_font, (WIDTH + 35, 58))

    def draw_next_piece(self, screen):
        next_piece_idx = self.get_next_piece()
        next_piece = SHAPES[next_piece_idx]
        next_color = next_piece_idx + 1

        preview_block = 12
        piece_w = len(next_piece[0]) * preview_block
        piece_h = len(next_piece) * preview_block
        box_w, box_h = 100, 40
        box_x, box_y = WIDTH + 10, 85

        offset_x = box_x + (box_w - piece_w) // 2
        offset_y = box_y + (box_h - piece_h) // 2

        for i in range(len(next_piece)):
            for j in range(len(next_piece[i])):
                if next_piece[i][j]:
                    pygame.draw.rect(screen, COLORS[next_color],
                                    (offset_x + j * preview_block,
                                     offset_y + i * preview_block,
                                     preview_block - 1, preview_block - 1))

    def draw_game_over(self, screen, font):
        game_over_text = font.render("GAME OVER", True, COLOR_RED)
        screen.blit(game_over_text, (WIDTH + 15, HEIGHT // 2))

    def draw(self, screen):
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, BORDER_COLOR, (0, 0, WIDTH, HEIGHT), 2)

        self.draw_board(screen)
        self.draw_current_piece(screen)

        font = pygame.font.Font(None, 24)
        self.draw_score_box(screen, font)
        self.draw_next_piece_box(screen, font)
        self.draw_next_piece(screen)

        if self.game_over:
            self.draw_game_over(screen, font)

        pygame.display.flip()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.game = Tetris(self.sound_manager)
        
        self.fall_time = 0
        self.last_left_time = 0
        self.last_right_time = 0
        self.last_down_time = 0
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

    def handle_keydown(self, event):
        if not self.game.game_over:
            if event.key == pygame.K_LEFT:
                self.game.move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.game.move(1, 0)
            elif event.key == pygame.K_DOWN:
                self.game.move(0, 1)
            elif event.key == pygame.K_SPACE:
                self.game.rotate()
            elif event.key == pygame.K_p:
                self.game.paused = not self.game.paused
        if event.key == pygame.K_r and self.game.game_over:
            self.game = Tetris(self.sound_manager)

    def handle_input(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and current_time - self.last_left_time > MOVE_DELAY:
            self.game.move(-1, 0)
            self.last_left_time = current_time

        if keys[pygame.K_RIGHT] and current_time - self.last_right_time > MOVE_DELAY:
            self.game.move(1, 0)
            self.last_right_time = current_time

        if keys[pygame.K_DOWN] and current_time - self.last_down_time > MOVE_DELAY:
            self.game.move(0, 1)
            self.last_down_time = current_time

    def update_game(self):
        self.fall_time += self.clock.get_rawtime()
        self.clock.tick()

        if self.fall_time >= FALL_SPEED:
            self.fall_time = 0
            self.game.move(0, 1)

    def run(self):
        while self.running:
            self.handle_events()

            if not self.game.game_over and not self.game.paused:
                self.handle_input()
                self.update_game()

            self.game.draw(self.screen)

        pygame.quit()


def main():
    Game().run()


if __name__ == "__main__":
    main()
