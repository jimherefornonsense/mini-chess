# A mini chess library.  

* Support real-time/regular chess  
* Support multiple sizes of chess board  
* Support piece delay movement to realize trevel time for moving from A to B  
* Be aware of the same color pieces collision will result as capture move when the board has been set delay more than 1  
* A winner when the other color's king piece is captured  

## Example
```
from mini_chess.mini_chess import MiniChess
from mini_chess.board_example import GARDNER_BOARD

if __name__ == "__main__":
    board = MiniChess(GARDNER_BOARD)
    print(board)

    print(list(board.generate_all_moves()))

    board.push("a2a3")
    board.update_time()
    print(board)
```  
```
$ rnbqk
  ppppp
  .....
  PPPPP
  RNBQK
  
$ ['a2a3', 'a2a2', 'b2b3', 'b2b2', 'c2c3', 'c2c2', 'd2d3', 'd2d2', 'e2e3', 'e2e2', 'a1a1', 'b1a3', 'b1c3', 'b1b1', 'c1c1', 'd1d1', 'e1e1']

$ rnbqk
  ppppp
  P....
  .PPPP
  RNBQK
```