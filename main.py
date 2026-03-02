import pygame
import random

pygame.init()

BLOCK_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = COLS * BLOCK_SIZE
HEIGHT = ROWS * BLOCK_SIZE
SCREEN_WIDTH = WIDTH + 200
SCREEN_HEIGHT = HEIGHT

BORDER_COLOR = (255, 0, 0)

COLORS = [
    (0, 0, 0),
    (0, 255, 255),
    (0, 0, 255),
    (255, 165, 0),
    (255, 255, 0),
    (0, 255, 0),
    (128, 0, 128),
    (255, 0, 0),
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

class Tetris:
    def __init__(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.new_piece()
        self.score = 0
        self.game_over = False
        self.paused = False

    def new_piece(self):
        self.piece_type = random.randint(0, len(SHAPES) - 1)
        self.piece = [row[:] for row in SHAPES[self.piece_type]]
        self.color = self.piece_type + 1
        self.x = 0
        self.y = 0

    def rotate(self):
        rotated = [list(row) for row in zip(*reversed(self.piece))]
        if not self.collision(rotated, self.x, self.y):
            self.piece = rotated

    def collision(self, piece, x, y):
        for row in range(len(piece)):
            for col in range(len(piece[row])):
                if piece[row][col]:
                    new_x = x + col
                    new_y = y + row
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                        return True
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return True
        return False

    def lock_piece(self):
        for row in range(len(self.piece)):
            for col in range(len(self.piece[row])):
                if self.piece[row][col]:
                    board_y = self.y + row
                    board_x = self.x + col
                    if board_y >= 0:
                        self.board[board_y][board_x] = self.color
        self.clear_lines()
        self.new_piece()
        if self.collision(self.piece, self.x, self.y):
            self.game_over = True

    def clear_lines(self):
        lines_cleared = 0
        for row in range(ROWS):
            if all(self.board[row]):
                self.board.pop(row)
                self.board.insert(0, [0] * COLS)
                lines_cleared += 1
        self.score += lines_cleared * 100

    def move(self, dx, dy):
        if not self.collision(self.piece, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        elif dy > 0:
            self.lock_piece()
        return False

    def draw(self, screen):
        screen.fill((20, 20, 40))
        
        pygame.draw.rect(screen, BORDER_COLOR, (0, 0, WIDTH, HEIGHT), 2)
        
        for y in range(ROWS):
            for x in range(COLS):
                if self.board[y][x]:
                    pygame.draw.rect(screen, COLORS[self.board[y][x]],
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
        
        for y in range(len(self.piece)):
            for x in range(len(self.piece[y])):
                if self.piece[y][x]:
                    pygame.draw.rect(screen, COLORS[self.color],
                                   ((self.x + x) * BLOCK_SIZE, (self.y + y) * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
        
        font = pygame.font.Font(None, 36)
        score_surface = font.render(f"Score: {self.score}", True, (255, 255, 255))
        pygame.draw.rect(screen, BORDER_COLOR, (WIDTH + 15, 45, score_surface.get_width() + 10, score_surface.get_height() + 10), 2)
        screen.blit(score_surface, (WIDTH + 20, 50))
        
        if self.game_over:
            game_over_text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(game_over_text, (WIDTH + 30, HEIGHT // 2))
        
        pygame.display.flip()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris()
    
    fall_time = 0
    fall_speed = 500
    move_delay = 100
    last_left_time = 0
    last_right_time = 0
    running = True
    
    while running:
        current_time = pygame.time.get_ticks()
        fall_time += clock.get_rawtime()
        clock.tick()
        
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not game.game_over:
                    if event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        game.move(0, 1)
                    elif event.key == pygame.K_SPACE:
                        game.rotate()
                    elif event.key == pygame.K_p:
                        game.paused = not game.paused
                if event.key == pygame.K_r and game.game_over:
                    game = Tetris()
        
        if not game.game_over and not game.paused:
            if fall_time >= fall_speed:
                fall_time = 0
                game.move(0, 1)
            
            if keys[pygame.K_LEFT] and current_time - last_left_time > move_delay:
                game.move(-1, 0)
                last_left_time = current_time
            
            if keys[pygame.K_RIGHT] and current_time - last_right_time > move_delay:
                game.move(1, 0)
                last_right_time = current_time
            
            if keys[pygame.K_DOWN]:
                game.move(0, 1)
        
        game.draw(screen)
    
    pygame.quit()

if __name__ == "__main__":
    main()
