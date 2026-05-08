#!/usr/bin/env python3
"""
Checkers (Draughts) Game
An 8x8 board game with alternating turns, standard capture and kinging rules.
Move notation: from-to positions (e.g., "e2-e4")
"""

import re
from enum import Enum
from typing import Optional


class Piece(Enum):
    RED = "r"
    BLACK = "b"
    RED_KING = "R"
    BLACK_KING = "B"


class Board:
    """8x8 Checkers board with piece management."""

    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self._initialize_pieces()

    def _initialize_pieces(self):
        """Place pieces in starting positions."""
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    # Black at top (rows 0-2), Red at bottom (rows 5-7)
                    if row < 3:
                        self.board[row][col] = Piece.BLACK
                    elif row > 4:
                        self.board[row][col] = Piece.RED

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get piece at given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        """Set piece at given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is valid and on a dark square."""
        return 0 <= row < 8 and 0 <= col < 8 and (row + col) % 2 == 1

    def display(self):
        """Display the board state."""
        print("  a b c d e f g h")
        print(" +-----------------+")
        for row in range(8):
            row_str = f"{row + 1}|"
            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    row_str += " |"
                elif piece == Piece.RED:
                    row_str += "R|"
                elif piece == Piece.RED_KING:
                    row_str += "K|"
                elif piece == Piece.BLACK:
                    row_str += "B|"
                else:
                    row_str += "Q|"
            print(row_str)
            print(" +-----------------+")


class Game:
    """Checkers game with turn management and rules."""

    def __init__(self):
        self.board = Board()
        self.current_player = Piece.RED
        self.game_over = False
        self.winner = None

    def switch_turn(self):
        """Switch to the other player."""
        self.current_player = Piece.BLACK if self.current_player == Piece.RED else Piece.RED

    def parse_move(self, move_str: str) -> tuple:
        """
        Parse move notation like 'e2-e4' into (from_row, from_col, to_row, to_col).
        Returns None if invalid.
        """
        pattern = r"^([a-h])([1-8])\s*-\s*([a-h])([1-8])$"
        match = re.match(pattern, move_str.strip())
        if not match:
            return None

        from_col = ord(match.group(1)) - ord('a')
        from_row = int(match.group(2)) - 1
        to_col = ord(match.group(3)) - ord('a')
        to_row = int(match.group(4)) - 1

        return (from_row, from_col, to_row, to_col)

    def is_valid_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> tuple:
        """
        Validate a move. Returns (is_valid, capture_info).
        capture_info is (captured_row, captured_col) if capture, else None.
        """
        piece = self.board.get_piece(from_row, from_col)
        if piece is None:
            return (False, None)

        # Check if it's the current player's piece
        if piece == Piece.RED or piece == Piece.RED_KING:
            if self.current_player != Piece.RED:
                return (False, None)
        else:
            if self.current_player != Piece.BLACK:
                return (False, None)

        # Calculate direction
        if piece == Piece.RED or piece == Piece.RED_KING:
            direction = -1  # Red moves up (decreasing row)
        else:
            direction = 1   # Black moves down (increasing row)

        # Regular move (1 square diagonally)
        if abs(to_row - from_row) == 1 and abs(to_col - from_col) == 1:
            if piece in (Piece.RED_KING, Piece.BLACK_KING):
                # Kings can move both directions
                if (to_row - from_row) in (-1, 1):
                    if self.board.get_piece(to_row, to_col) is None:
                        return (True, None)
            else:
                # Regular pieces move forward only
                if (to_row - from_row) == direction:
                    if self.board.get_piece(to_row, to_col) is None:
                        return (True, None)

        # Capture move (2 squares diagonally)
        if abs(to_row - from_row) == 2 and abs(to_col - from_col) == 2:
            mid_row = (from_row + to_row) // 2
            mid_col = (from_col + to_col) // 2
            mid_piece = self.board.get_piece(mid_row, mid_col)

            if mid_piece is None:
                return (False, None)

            # Check if capturing opponent
            if piece in (Piece.RED, Piece.RED_KING):
                if mid_piece in (Piece.BLACK, Piece.BLACK_KING):
                    return (True, (mid_row, mid_col))
            else:
                if mid_piece in (Piece.RED, Piece.RED_KING):
                    return (True, (mid_row, mid_col))

        return (False, None)

    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """
        Execute a move. Returns True if successful.
        """
        piece = self.board.get_piece(from_row, from_col)

        # Move the piece
        self.board.set_piece(to_row, to_col, piece)
        self.board.set_piece(from_row, from_col, None)

        # Check for capture
        if abs(to_row - from_row) == 2:
            mid_row = (from_row + to_row) // 2
            mid_col = (from_col + to_col) // 2
            self.board.set_piece(mid_row, mid_col, None)

        # Kinging
        if piece == Piece.RED and to_row == 0:
            self.board.set_piece(to_row, to_col, Piece.RED_KING)
        elif piece == Piece.BLACK and to_row == 7:
            self.board.set_piece(to_row, to_col, Piece.BLACK_KING)

        return True

    def check_win(self):
        """Check if someone has won."""
        red_count = 0
        black_count = 0

        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece == Piece.RED or piece == Piece.RED_KING:
                    red_count += 1
                elif piece == Piece.BLACK or piece == Piece.BLACK_KING:
                    black_count += 1

        if red_count == 0:
            self.game_over = True
            self.winner = Piece.BLACK
        elif black_count == 0:
            self.game_over = True
            self.winner = Piece.RED

    def display(self):
        """Display current game state."""
        self.board.display()
        player_name = "Red" if self.current_player == Piece.RED else "Black"
        print(f"\nCurrent turn: {player_name}")
        if self.game_over:
            winner_name = "Red" if self.winner == Piece.RED else "Black"
            print(f"\nGame Over! {winner_name} wins!")

    def play(self):
        """Main game loop."""
        print("Welcome to Checkers!")
        print("Enter moves in format: a1-c3 (from-to)")
        print("Type 'quit' to end the game.\n")

        while not self.game_over:
            self.display()

            move_str = input(f"\n{self.current_player.name} player, enter your move: ").strip()

            if move_str.lower() == "quit":
                print("Game ended by player.")
                break

            parsed = self.parse_move(move_str)
            if parsed is None:
                print("Invalid move format. Use: a1-c3")
                continue

            from_row, from_col, to_row, to_col = parsed

            is_valid, capture = self.is_valid_move(from_row, from_col, to_row, to_col)

            if not is_valid:
                print("Invalid move!")
                continue

            self.make_move(from_row, from_col, to_row, to_col)
            self.check_win()

            if not self.game_over:
                self.switch_turn()

        self.display()
        if self.winner:
            winner_name = "Red" if self.winner == Piece.RED else "Black"
            print(f"\n{winner_name} wins!")


if __name__ == "__main__":
    game = Game()
    game.play()
