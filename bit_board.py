"""
Bit digit on board
+---+---+---+---+---+
|  0|  1|  2|  3|  4|
+---+---+---+---+---+
|  5|  6|  7|  8|  9|
+---+---+---+---+---+
| 10| 11| 12| 13| 14|
+---+---+---+---+---+
| 15| 16| 17| 18| 19|
+---+---+---+---+---+
| 20| 21| 22| 23| 24|
+---+---+---+---+---+
"""

from .const import *

def print_mask(mask):
    mask_str = (bin(mask)[2:])[::-1]
    bit_mask = [mask_str[i:i+BOARD_COL] for i in range(0, len(mask_str), BOARD_COL)]
    bit_mask = "\n".join(bit_mask)

    print(bit_mask)

class BitBoard:
    def __init__(self, board):
        self.board_mask = [((1 << BOARD_COL) - 1) << (y * BOARD_COL) for y in range(BOARD_ROW)]
        # Initialize the board with starting positions
        self.white_pieces = 0
        self.black_pieces = 0

        for y in range(BOARD_ROW):
            for x in range(BOARD_COL):
                piece = board[y][x]
                if piece == ".":
                    continue

                # Set the corresponding bit in the bitboard
                bit_digit = y * BOARD_COL + x
                if piece.isupper():
                    self.white_pieces |= (1 << bit_digit)
                else:
                    self.black_pieces |= (1 << bit_digit)

    def __str__(self):
        board_str = (bin(self.white_pieces | self.black_pieces)[2:])[::-1]
        bit_board = [board_str[i:i+BOARD_COL] for i in range(0, len(board_str), BOARD_COL)]
        bit_board = "\n".join(bit_board)
        
        return bit_board

    def mirror(self, board):
        mirrored_board = 0
        mid_index = len(self.board_mask) // 2
        even = 1 if (len(self.board_mask) % 2 == 0) else 0

        for i, row in enumerate(self.board_mask):
            if i <= mid_index:
                mirrored_board |= (board & row) << (BOARD_COL * (mid_index - i) * 2 + even)
            else:
                mirrored_board |= (board & row) >> (BOARD_COL * (i - mid_index) * 2 - even)

        return mirrored_board

    def make_move(self, from_x, from_y, to_x, to_y):
        # Compute the bit indices of the source and destination squares
        from_bit_digit = from_y * BOARD_COL + from_x
        to_bit_digit = to_y * BOARD_COL + to_x
        
        # Remove the source piece from the bitboard
        is_white = False
        if self.white_pieces & (1 << from_bit_digit):
            self.white_pieces &= ~(1 << from_bit_digit)
            is_white = True
        else:
            self.black_pieces &= ~(1 << from_bit_digit)

        # Add the destination piece to the bitboard
        if is_white:
            self.white_pieces |= (1 << to_bit_digit)
            self.black_pieces &= ~(1 << to_bit_digit)
        else:
            self.black_pieces |= (1 << to_bit_digit)
            self.white_pieces &= ~(1 << to_bit_digit)

    def digit_to_coords(self, digit):
        return (digit % BOARD_COL, digit // BOARD_ROW)

    def generate_valid_moves(self, x, y, piece):
        bit_digit = y * BOARD_COL + x
        board = self.white_pieces | self.black_pieces
        enemy = self.black_pieces

        assert (1 << bit_digit) & board, "No piece found at the given bit!"

        if self.black_pieces & (1 << bit_digit):        
            mirrored_white = self.mirror(self.white_pieces)
            mirrored_black = self.mirror(self.black_pieces)
            bit_digit = (BOARD_ROW - y - 1) * BOARD_COL + x
            board = mirrored_white | mirrored_black
            enemy = mirrored_white
        
        moves = 0
        if piece == 'p':
            moves = self.pawn_valid_moves(bit_digit, board, enemy)
        elif piece == 'r':
            moves = self.rook_valid_moves(bit_digit, board, enemy)
        elif piece == 'n':
            moves = self.knight_valid_moves(bit_digit, board, enemy)
        elif piece == 'b':
            moves = self.bishop_valid_moves(bit_digit, board, enemy)
        elif piece == 'q':
            moves = self.queen_valid_moves(bit_digit, board, enemy)
        elif piece == 'k':
            moves = self.king_valid_moves(bit_digit, board, enemy)
        
        bit_at = 0
        while moves != 0:
            if moves & 1:
                yield self.digit_to_coords(bit_at)
            moves = moves >> 1
            bit_at += 1

    # All mask calculations are using positions of the player's perspective

    def get_fence_mask(self):
        left_fence = 0
        right_fence = 0
        for row in self.board_mask:
            bin_str = bin(row)[2:]
            left_1_bit_at = bin_str.find('1')
            right_fence |= int("1" + "0" * (len(bin_str) - (left_1_bit_at + 1)), 2)
            right_1_bit_at = bin_str.rfind('1')
            left_fence |= int(bin_str[right_1_bit_at:], 2)
        
        return left_fence, right_fence
    
    # Contain the complement bits in the board's size
    def get_bits_complement(self, bits):
        return ~bits & sum(self.board_mask)

    def pawn_valid_moves(self, bit_digit, board, enemy):
        pos = 1 << bit_digit
        move_mask = 0
        attack_mask = 0

        if (pos >> BOARD_COL) & self.get_bits_complement(board):
            move_mask |= pos >> BOARD_COL 
            # Two steps forward when at its default position
            if pos & self.board_mask[-2] and (move_mask >> BOARD_COL) & self.get_bits_complement(board):
                move_mask |= move_mask >> BOARD_COL

        left_fence, right_fence = self.get_fence_mask()

        # Attack moves
        if pos & self.get_bits_complement(left_fence):
            attack_mask |= pos >> (BOARD_COL + 1)
        if pos & self.get_bits_complement(right_fence):
            attack_mask |= pos >> (BOARD_COL - 1)
        attack_mask &= enemy

        return (move_mask | attack_mask) & sum(self.board_mask)
    
    def knight_valid_moves(self, bit_digit, board, enemy):
        pos = 1 << bit_digit
        move_mask = 0
        attack_mask = 0

        left_fence, right_fence = self.get_fence_mask()

        # * . *
        # . . .
        #   N
        to_up = 0
        if pos & self.get_bits_complement(left_fence):
            to_up |= (pos >> (BOARD_COL * 2)) >> 1
        if pos & self.get_bits_complement(right_fence):
            to_up |= (pos >> (BOARD_COL * 2)) << 1
        move_mask |= to_up & self.get_bits_complement(board)
        attack_mask |= to_up & enemy

        #   N
        # . . .
        # * . *
        to_down = 0
        if pos & self.get_bits_complement(left_fence): 
            to_down |= (pos << (BOARD_COL * 2)) >> 1
        if pos & self.get_bits_complement(right_fence):
            to_down |= (pos << (BOARD_COL * 2)) << 1
        move_mask |= to_down & self.get_bits_complement(board)
        attack_mask |= to_down & enemy

        valid_row_bits = self.board_mask[bit_digit // BOARD_ROW]
        
        # * . . 
        # . . . N
        # * . .
        to_left = ((pos >> 2) & valid_row_bits) >> BOARD_COL
        to_left |= ((pos >> 2) & valid_row_bits) << BOARD_COL
        move_mask |= to_left & self.get_bits_complement(board)
        attack_mask |= to_left & enemy

        #   . . *
        # N . . .
        #   . . *
        to_right = ((pos << 2) & valid_row_bits) >> BOARD_COL
        to_right |= ((pos << 2) & valid_row_bits) << BOARD_COL
        move_mask |= to_right & self.get_bits_complement(board)
        attack_mask |= to_right & enemy

        return (move_mask | attack_mask) & sum(self.board_mask)        
    
    def king_valid_moves(self, bit_digit, board, enemy):
        pos = 1 << bit_digit
        move_mask = 0
        attack_mask = 0

        left_fence, right_fence = self.get_fence_mask()

        if pos & self.get_bits_complement(left_fence):
            # Up left
            move_mask |= (pos >> (BOARD_COL + 1)) & self.get_bits_complement(board)
            attack_mask |= (pos >> (BOARD_COL + 1)) & enemy
            # Left
            move_mask |= (pos >> 1) & self.get_bits_complement(board)
            attack_mask |= (pos >> 1) & enemy
            # Down left
            move_mask |= (pos << (BOARD_COL - 1)) & self.get_bits_complement(board)
            attack_mask |= (pos << (BOARD_COL - 1)) & enemy

        # Up
        move_mask |= (pos >> BOARD_COL) & self.get_bits_complement(board)
        attack_mask |= pos >> (BOARD_COL) & enemy
        # Down
        move_mask |= (pos << BOARD_COL) & self.get_bits_complement(board)
        attack_mask |= pos << (BOARD_COL) & enemy

        if pos & self.get_bits_complement(right_fence):
            # Up right
            move_mask |= (pos >> (BOARD_COL - 1)) & self.get_bits_complement(board)
            attack_mask |= (pos >> (BOARD_COL - 1)) & enemy
            # Right
            move_mask |= (pos << 1) & self.get_bits_complement(board)
            attack_mask |= (pos << 1) & enemy
            # Down right
            move_mask |= (pos << (BOARD_COL + 1)) & self.get_bits_complement(board)
            attack_mask |= (pos << (BOARD_COL + 1)) & enemy

        return (move_mask | attack_mask) & sum(self.board_mask)

    def row_valid_moves(self, bit_digit, board, enemy):
        pos = 1 << bit_digit
        valid_row_bits = pos ^ self.board_mask[bit_digit // BOARD_ROW]
        move_mask = 0
        attack_mask = 0

        to_left = pos >> 1
        while to_left & valid_row_bits:
            if to_left & board:
                if to_left & enemy:
                    attack_mask |= to_left
                break
            move_mask |= to_left
            to_left >>= 1

        to_right = pos << 1 
        while to_right & valid_row_bits:
            if to_right & board:
                if to_right & enemy:
                    attack_mask |= to_right
                break
            move_mask |= to_right
            to_right <<= 1
        
        return move_mask, attack_mask

    def col_valid_moves(self, bit_digit, board, enemy):
        pos = 1 << bit_digit
        move_mask = 0
        attack_mask = 0

        to_up = pos >> BOARD_COL
        while to_up & sum(self.board_mask):
            if to_up & board:
                if to_up & enemy:
                    attack_mask |= to_up
                break
            move_mask |= to_up
            to_up >>= BOARD_COL

        to_down = pos << BOARD_COL
        while to_down & sum(self.board_mask):
            if to_down & board:
                if to_down & enemy:
                    attack_mask |= to_down
                break
            move_mask |= to_down
            to_down <<= BOARD_COL
        
        return move_mask, attack_mask

    def diag_valid_moves(self, bit_digit, board, enemy):
        pos = 1 << bit_digit
        move_mask = 0
        attack_mask = 0

        left_fence, right_fence = self.get_fence_mask()

        to_up_left = pos
        while to_up_left & self.get_bits_complement(left_fence):
            to_up_left >>= BOARD_COL + 1
            if to_up_left & board:
                if to_up_left & enemy:
                    attack_mask |= to_up_left
                break
            move_mask |= to_up_left

        to_up_right = pos
        while to_up_right & self.get_bits_complement(right_fence):
            to_up_right >>= BOARD_COL - 1
            if to_up_right & board:
                if to_up_right & enemy:
                    attack_mask |= to_up_right
                break
            move_mask |= to_up_right

        to_down_left = pos
        while to_down_left & self.get_bits_complement(left_fence):
            to_down_left <<= BOARD_COL - 1
            if to_down_left & board:
                if to_down_left & enemy:
                    attack_mask |= to_down_left
                break
            move_mask |= to_down_left

        to_down_right = pos
        while to_down_right & self.get_bits_complement(right_fence):
            to_down_right <<= BOARD_COL + 1
            if to_down_right & board:
                if to_down_right & enemy:
                    attack_mask |= to_down_right
                break
            move_mask |= to_down_right

        
        return move_mask, attack_mask

    def rook_valid_moves(self, bit_digit, board, enemy):
        move_mask = 0
        attack_mask = 0

        # Row moves
        mk, ak = self.row_valid_moves(bit_digit, board, enemy)
        move_mask |= mk
        attack_mask |= ak
        
        # Col moves
        mk, ak = self.col_valid_moves(bit_digit, board, enemy)
        move_mask |= mk
        attack_mask |= ak

        return (move_mask | attack_mask) & sum(self.board_mask)
    
    def bishop_valid_moves(self, bit_digit, board, enemy):
        move_mask = 0
        attack_mask = 0

        # Diagonal moves
        mk, ak = self.diag_valid_moves(bit_digit, board, enemy)
        move_mask |= mk
        attack_mask |= ak

        return (move_mask | attack_mask) & sum(self.board_mask)
    
    def queen_valid_moves(self, bit_digit, board, enemy):
        move_mask = 0
        attack_mask = 0

        mk, ak = self.row_valid_moves(bit_digit, board, enemy)
        move_mask |= mk
        attack_mask |= ak

        mk, ak = self.col_valid_moves(bit_digit, board, enemy)
        move_mask |= mk
        attack_mask |= ak

        mk, ak = self.diag_valid_moves(bit_digit, board, enemy)
        move_mask |= mk
        attack_mask |= ak

        return (move_mask | attack_mask) & sum(self.board_mask)