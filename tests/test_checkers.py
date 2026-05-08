#!/usr/bin/env python3
"""Tests for the Checkers game."""

import unittest
from checkers import Board, Game, Piece


class TestBoard(unittest.TestCase):
    """Tests for the Board class."""

    def setUp(self):
        self.board = Board()

    def test_initialization(self):
        """Test that the board is initialized with pieces in correct positions."""
        # Black pieces should be in rows 0-2 (top)
        self.assertIsNotNone(self.board.get_piece(0, 1))
        self.assertEqual(self.board.get_piece(0, 1), Piece.BLACK)

        # Red pieces should be in rows 5-7 (bottom)
        self.assertIsNotNone(self.board.get_piece(5, 0))
        self.assertEqual(self.board.get_piece(5, 0), Piece.RED)

    def test_get_piece_out_of_bounds(self):
        """Test that out of bounds positions return None."""
        self.assertIsNone(self.board.get_piece(-1, 0))
        self.assertIsNone(self.board.get_piece(8, 0))
        self.assertIsNone(self.board.get_piece(0, 8))

    def test_set_piece(self):
        """Test setting and getting a piece."""
        self.board.set_piece(3, 4, Piece.RED)
        self.assertEqual(self.board.get_piece(3, 4), Piece.RED)

        self.board.set_piece(3, 4, None)
        self.assertIsNone(self.board.get_piece(3, 4))


class TestGame(unittest.TestCase):
    """Tests for the Game class."""

    def setUp(self):
        self.game = Game()

    def test_initial_player(self):
        """Test that Red starts first."""
        self.assertEqual(self.game.current_player, Piece.RED)

    def test_parse_move_valid(self):
        """Test parsing valid move notation."""
        result = self.game.parse_move("a1-c3")
        self.assertEqual(result, (0, 0, 2, 2))

        result = self.game.parse_move("e2-e4")
        self.assertEqual(result, (1, 4, 3, 4))

        result = self.game.parse_move("h7-f5")
        self.assertEqual(result, (6, 7, 4, 5))

    def test_parse_move_invalid_format(self):
        """Test parsing invalid move notation."""
        self.assertIsNone(self.game.parse_move("a1"))
        self.assertIsNone(self.game.parse_move("a1-c"))
        self.assertIsNone(self.game.parse_move("a1-c3-5"))
        self.assertIsNone(self.game.parse_move("i1-k3"))

    def test_parse_move_whitespace(self):
        """Test parsing move with extra whitespace."""
        result = self.game.parse_move("a1 - c3")
        self.assertEqual(result, (0, 0, 2, 2))

    def test_valid_red_move(self):
        """Test valid diagonal move for Red."""
        # Setup: clear path for Red to move from a3 to b2 (Red moves UP - row decreases)
        self.game.board.set_piece(2, 0, Piece.RED)
        self.game.board.set_piece(1, 1, None)

        is_valid, capture = self.game.is_valid_move(2, 0, 1, 1)
        self.assertTrue(is_valid)
        self.assertIsNone(capture)

    def test_valid_black_move(self):
        """Test valid diagonal move for Black."""
        # Setup: clear path for Black to move from h4 to g5 (Black moves DOWN - row increases)
        self.game.board.set_piece(3, 7, Piece.BLACK)
        self.game.board.set_piece(4, 6, None)
        # Set current player to Black for this test
        self.game.current_player = Piece.BLACK

        is_valid, capture = self.game.is_valid_move(3, 7, 4, 6)
        self.assertTrue(is_valid)
        self.assertIsNone(capture)

    def test_invalid_move_wrong_player(self):
        """Test that you can't move opponent's piece."""
        # Try to move Black piece (0,1) when it's Red's turn
        is_valid, capture = self.game.is_valid_move(0, 1, 1, 2)
        self.assertFalse(is_valid)

    def test_invalid_move_diagonal(self):
        """Test that non-diagonal moves are invalid."""
        self.game.board.set_piece(3, 4, Piece.RED)
        is_valid, capture = self.game.is_valid_move(3, 4, 3, 5)
        self.assertFalse(is_valid)

    def test_capture_move(self):
        """Test valid capture move."""
        # Setup: Red at a2, Black at b3, empty at c4
        self.game.board.set_piece(1, 0, Piece.RED)
        self.game.board.set_piece(2, 1, Piece.BLACK)
        self.game.board.set_piece(3, 2, None)

        is_valid, capture = self.game.is_valid_move(1, 0, 3, 2)
        self.assertTrue(is_valid)
        self.assertIsNotNone(capture)
        self.assertEqual(capture, (2, 1))

    def test_no_capture_empty_jump(self):
        """Test that jumping over empty square is invalid."""
        self.game.board.set_piece(1, 0, Piece.RED)
        # Clear the mid square (2,1) to simulate empty
        self.game.board.set_piece(2, 1, None)
        self.game.board.set_piece(3, 2, None)

        is_valid, capture = self.game.is_valid_move(1, 0, 3, 2)
        self.assertFalse(is_valid)

    def test_kinging_red(self):
        """Test Red piece becomes king at row 0."""
        self.game.board.set_piece(1, 0, Piece.RED)
        self.game.make_move(1, 0, 0, 1)
        self.assertEqual(self.game.board.get_piece(0, 1), Piece.RED_KING)

    def test_kinging_black(self):
        """Test Black piece becomes king at row 7."""
        self.game.board.set_piece(6, 7, Piece.BLACK)
        self.game.make_move(6, 7, 7, 6)
        self.assertEqual(self.game.board.get_piece(7, 6), Piece.BLACK_KING)

    def test_red_cannot_move_backwards(self):
        """Test that Red pieces can't move backwards."""
        self.game.board.set_piece(2, 1, Piece.RED)
        is_valid, capture = self.game.is_valid_move(2, 1, 3, 2)
        self.assertFalse(is_valid)

    def test_black_cannot_move_forward(self):
        """Test that Black pieces can't move forwards (toward row 0)."""
        self.game.board.set_piece(5, 0, Piece.BLACK)
        is_valid, capture = self.game.is_valid_move(5, 0, 4, 1)
        self.assertFalse(is_valid)


class TestGameWinCondition(unittest.TestCase):
    """Tests for win conditions."""

    def test_no_win_initial(self):
        """Test that game is not over at start."""
        game = Game()
        self.assertFalse(game.game_over)

    def test_win_when_all_red_captured(self):
        """Test Black wins when all Red pieces are captured."""
        game = Game()
        # Capture all Red pieces
        for row in range(8):
            for col in range(8):
                piece = game.board.get_piece(row, col)
                if piece == Piece.RED or piece == Piece.RED_KING:
                    game.board.set_piece(row, col, None)

        game.check_win()
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, Piece.BLACK)

    def test_win_when_all_black_captured(self):
        """Test Red wins when all Black pieces are captured."""
        game = Game()
        # Capture all Black pieces
        for row in range(8):
            for col in range(8):
                piece = game.board.get_piece(row, col)
                if piece == Piece.BLACK or piece == Piece.BLACK_KING:
                    game.board.set_piece(row, col, None)

        game.check_win()
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, Piece.RED)


if __name__ == "__main__":
    unittest.main()
