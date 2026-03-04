import pytest
import sys
sys.path.insert(0, '.')

import pygame
pygame.init()

from main import Tetris, COLS, ROWS, SHAPES, COLORS


class TestTetrisInit:
    def setup_method(self):
        self.game = Tetris()

    def test_initializes_with_empty_board(self):
        for i in range(ROWS):
            for j in range(COLS):
                assert self.game.board[i][j] == 0

    def test_initializes_with_piece_queue(self):
        assert len(self.game.piece_queue) == 2

    def test_initializes_with_score_zero(self):
        assert self.game.score == 0

    def test_initializes_not_game_over(self):
        assert self.game.game_over is False

    def test_initializes_not_paused(self):
        assert self.game.paused is False


class TestCollision:
    def setup_method(self):
        self.game = Tetris()

    def test_empty_board_no_collision_at_origin(self):
        piece = [[1, 1], [1, 1]]
        assert self.game.collision(piece, 0, 0) is False

    def test_collision_out_of_bounds_left(self):
        piece = [[1, 1, 1]]
        assert self.game.collision(piece, -1, 0) is True

    def test_collision_out_of_bounds_right(self):
        piece = [[1, 1, 1, 1]]
        assert self.game.collision(piece, COLS - 1, 0) is True

    def test_collision_out_of_bounds_bottom(self):
        piece = [[1]]
        assert self.game.collision(piece, 0, ROWS) is True

    def test_collision_with_locked_piece(self):
        self.game.board[ROWS - 1][0] = 1
        piece = [[1]]
        assert self.game.collision(piece, 0, ROWS - 1) is True


class TestMovement:
    def setup_method(self):
        self.game = Tetris()
        self.game.x = 5
        self.game.y = 10

    def test_move_left_from_origin(self):
        self.game.move(-1, 0)
        assert self.game.x == 4

    def test_move_right_from_origin(self):
        self.game.move(1, 0)
        assert self.game.x == 6

    def test_move_down_from_origin(self):
        self.game.move(0, 1)
        assert self.game.y == 11


class TestRotation:
    def setup_method(self):
        self.game = Tetris()

    def test_rotate_t_piece(self):
        self.game.piece = [[1, 1, 1], [0, 1, 0]]
        self.game.rotate()
        assert self.game.piece == [[0, 1], [1, 1], [0, 1]]

    def test_rotate_line_piece(self):
        self.game.piece = [[1, 1, 1, 1]]
        self.game.rotate()
        assert self.game.piece == [[1], [1], [1], [1]]

    def test_rotate_square_piece(self):
        self.game.piece = [[1, 1], [1, 1]]
        self.game.rotate()
        assert self.game.piece == [[1, 1], [1, 1]]


class TestClearLines:
    def setup_method(self):
        self.game = Tetris()

    def test_clear_single_full_line(self):
        for j in range(COLS):
            self.game.board[ROWS - 1][j] = 1
        self.game.clear_lines()
        assert self.game.score == 100

    def test_clear_multiple_full_lines(self):
        for j in range(COLS):
            self.game.board[ROWS - 1][j] = 1
            self.game.board[ROWS - 2][j] = 1
        self.game.clear_lines()
        assert self.game.score == 200


class TestNewPiece:
    def setup_method(self):
        self.game = Tetris()

    def test_new_piece_from_queue(self):
        self.game.piece_queue = [0, 1]
        self.game.new_piece()
        assert self.game.piece_type == 0
        assert len(self.game.piece_queue) == 2

    def test_new_piece_has_valid_shape(self):
        self.game.new_piece()
        assert self.game.piece in SHAPES


class TestGetNextPiece:
    def setup_method(self):
        self.game = Tetris()

    def test_returns_next_in_queue(self):
        self.game.piece_queue = [3, 5]
        assert self.game.get_next_piece() == 3
