import copy

from .bit_board import BitBoard
from .const import *
from collections import deque

class MiniChess(BitBoard):
    def __init__(self, board, move_time = 1):
        self._turn = 0
        # Initialize the board with starting positions
        self._board = board
        # Moving queue for pieces
        self._moving_queue = deque()
        self._move_time = move_time
        self._time = 0
        super().__init__(self._board)

    def __str__(self):
        # Convert the board to a printable string
        return "\n".join(self._board)
    
    def cur_color(self, color):
        """ Input "w" for white, "b" for black """
        if color == "w":
            self._turn = 0
        elif color == "b":
            self._turn = 1

    def mirror_coords(self, x, y):
        return x, BOARD_ROW - (y + 1) 

    def move_to_coords(self, move):
        # Convert the move to board coordinates
        from_x = ord(move[0]) - ord("a")
        from_y = BOARD_ROW - int(move[1])
        to_x = ord(move[2]) - ord("a")
        to_y = BOARD_ROW - int(move[3])

        return from_x, from_y, to_x, to_y

    def coords_to_move(self, from_x, from_y, to_x, to_y):
        # Convert the coordinates to standard algebraic notation
        from_col = chr(ord("a") + from_x)
        from_row = str(BOARD_ROW - from_y)
        to_col = chr(ord("a") + to_x)
        to_row = str(BOARD_ROW - to_y)

        return from_col + from_row + to_col + to_row

    def is_legal_move(self, move):
        # Check if the given move is legal
        if move not in self.generate_all_moves():
            print("Invalid move!")
            return False
        # if self.leaves_king_in_check(move):
        #     print("King in check!")
        #     return False
        return True

    # def make_move(self, move):
    #     # Convert the move to board coordinates
    #     from_x, from_y, to_x, to_y = self.move_to_coords(move)
    #     if self._turn == 1:
    #         from_x, from_y = self.mirror_coords(from_x, from_y)
    #         to_x, to_y = self.mirror_coords(to_x, to_y)

    #     # Update bitboard
    #     super().make_move(from_x, from_y, to_x, to_y)

    #     # Make the move on the board
    #     self._board[to_y] = (
    #         self._board[to_y][:to_x]
    #         + self._board[from_y][from_x]
    #         + self._board[to_y][to_x + 1 :]
    #     )
    #     self._board[from_y] = (
    #         self._board[from_y][:from_x]
    #         + "."
    #         + self._board[from_y][from_x + 1 :]
    #     )
        
    #     self.check_queen_promotion(to_x, to_y)
        
    def parse_move(self, move):
        # Convert the move to board coordinates
        from_x, from_y, to_x, to_y = self.move_to_coords(move)
        if self._turn == 1:
            from_x, from_y = self.mirror_coords(from_x, from_y)
            to_x, to_y = self.mirror_coords(to_x, to_y)
        
        piece = self._board[from_y][from_x]
        
        return piece, (from_x, from_y), (to_x, to_y)
    
    def piece_up(self, from_x, from_y):
        # Update bitboard
        super().piece_up(from_x, from_y)
        
        # Take the piece from the board
        self._board[from_y] = (
            self._board[from_y][:from_x]
            + "."
            + self._board[from_y][from_x + 1 :]
        )
        
    def piece_down(self, to_x, to_y, piece, is_white):
        # Update bitboard
        super().piece_down(to_x, to_y, is_white)
        
        # Make the move on the board
        self._board[to_y] = (
            self._board[to_y][:to_x]
            + piece
            + self._board[to_y][to_x + 1 :]
        )
        self.check_queen_promotion(to_x, to_y)
    
    def push(self, move):
        if not self.is_legal_move(move):
            return False
        
        if move[:2] != move[2:]:        
            piece, from_coord, to_coord = self.parse_move(move)
            moving_piece = {"color": self._turn,
                            "from_coord": from_coord,
                            "to_coord": to_coord,
                            "piece": piece,
                            "time_at": self._time + self._move_time}
            
            self.piece_up(from_coord[0], from_coord[1])
            self._moving_queue.append(moving_piece)
            # self.make_move(move)
            
        return True
        
    def update_time(self):
        self._time += 1
        if len(self._moving_queue) != 0 and self._moving_queue[0]["time_at"] == self._time:
            moving_piece = self._moving_queue.popleft()
            is_white = True if moving_piece["color"] == 0 else False
            from_x, from_y = moving_piece["from_coord"]
            to_x, to_y = moving_piece["to_coord"]
            piece = moving_piece["piece"]
            
            self.piece_down(to_x, to_y, piece, is_white)
            
            if not is_white:
                from_x, from_y = self.mirror_coords(from_x, from_y)
                to_x, to_y = self.mirror_coords(to_x, to_y)
            
            uci = self.coords_to_move(from_x, from_y, to_x, to_y)
            return (uci, moving_piece["piece"])
        else:
            return None
    
    def check_queen_promotion(self, x, y):
        if y == 0:
            if self._board[y][x] == "P":
                self._board[y] = (
                    self._board[y][:x]
                    + "Q"
                    + self._board[y][x + 1 :]
                )
        if y == 4:
            if self._board[y][x] == "p":
                self._board[y] = (
                    self._board[y][:x]
                    + "q"
                    + self._board[y][x + 1 :]
                )

    def get_king(self, color):
        """ Input 0 for white, 1 for black """
        king = "K" if color == 0 else "k"

        # Find the king of the given color
        for from_y in range(BOARD_ROW):
            for from_x in range(BOARD_COL):
                piece = self._board[from_y][from_x]
                if piece == king:
                    return from_x, from_y
        
        assert True, "There's no king on the board."

    def is_in_check(self, color):
        """ Input 0 for white, 1 for black """
        # Check if the current player is in check
        king_x, king_y = self.get_king(color)

        # Get the opponent's valid moves
        self.cur_color("b" if color == 0 else "w")
        valid_moves = set(self.generate_all_moves())

        # Convert king's pos to black's relative pos if the opponent is black
        if self._turn == 1:
            king_x, king_y = self.mirror_coords(king_x, king_y)

        for y in range(BOARD_ROW):
            for x in range(BOARD_COL):
                from_x = x
                from_y = y
                if self._turn == 1:
                    from_x, from_y = self.mirror_coords(from_x, from_y)

                move = self.coords_to_move(from_x, from_y, king_x, king_y)

                if move in valid_moves:
                    return True
        return False

    def leaves_king_in_check(self, move):
        # Check if the move leaves the current player's king in check
        temp_board = copy.deepcopy(self)
        temp_board.make_move(move)

        return temp_board.is_in_check(self._turn)
    
    def piece_at(self, uci):
        """Piece at UCI coords"""
        x = ord(uci[0]) - ord("a")
        y = BOARD_ROW - int(uci[1])
        if self._turn == 1:
            x, y = self.mirror_coords(x, y)

        return self._board[y][x]
    
    def piece_map(self):
        # Stale pieces
        for y in range(BOARD_ROW):
            for x in range(BOARD_COL):
                piece = self._board[y][x]
                if piece == ".":
                    continue
                mirror_x, mirror_y = self.mirror_coords(x, y)
                yield mirror_x, mirror_y
        
        # Moving pieces
        for i in len(self._moving_queue):
            mirror_x, mirror_y = self.mirror_coords(self._moving_queue[i]["to_coord"])
            yield mirror_x, mirror_y
            

    def generate_all_moves(self):
        # Loop over all board positions
        for y in range(BOARD_ROW):
            for x in range(BOARD_COL):
                piece = self._board[y][x]
                if piece != ".":
                    # Filter pieces by color
                    if (self._turn == 0 and piece.isupper()):
                        # Generate moves for the current piece
                        valid_moves = self.generate_valid_moves(x, y, piece.lower())
                        for move in valid_moves:
                            yield self.coords_to_move(x, y, move[0], move[1])
                    elif (self._turn == 1 and piece.islower()):
                        # Generate moves for the current piece
                        valid_moves = self.generate_valid_moves(x, y, piece.lower())
                        for move in valid_moves:
                            mirror_x, mirror_y = self.mirror_coords(x, y)
                            yield self.coords_to_move(mirror_x, mirror_y, move[0], move[1])