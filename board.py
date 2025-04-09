from base import HexBoard as HexBoardBase


class HexBoard(HexBoardBase):
    def __init__(self, size: int):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
    
    def clone(self):
        """Devuelve una copia del tablero actual"""
        new_board = HexBoard(self.size)
        new_board.board = [row[:] for row in self.board]
        return new_board
    
    def place_piece(self, row: int, col: int, player_id: int) -> bool:
        """Coloca una ficha si la casilla está vacía."""
        if 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == 0:
            self.board[row][col] = player_id
            return True
        return False
    
    def get_possible_moves(self) -> list:
        """Devuelve todas las casillas vacías como tuplas (fila, columna)."""
        moves = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    moves.append((i, j))
        return moves
    
    def check_connection(self, player_id: int) -> bool:
        """Verifica si el jugador ha conectado sus dos lados"""
        if player_id == 1:
            visited = set()
            for i in range(self.size):
                if self.board[i][0] == player_id and (i, 0) not in visited:
                    if self._dfs_connection(i, 0, player_id, visited, is_horizontal=True):
                        return True
        else:
            visited = set()

            for j in range(self.size):
                if self.board[0][j] == player_id and (0, j) not in visited:
                    if self._dfs_connection(0, j, player_id, visited, is_horizontal=False):
                        return True
        
        return False
    
    def _dfs_connection(self, i, j, player_id, visited, is_horizontal):
        visited.add((i, j))
        
        if (is_horizontal and j == self.size - 1) or (not is_horizontal and i == self.size - 1):
            return True
        
        neighbors = self._get_neighbors(i, j)
        
        for ni, nj in neighbors:
            if 0 <= ni < self.size and 0 <= nj < self.size and \
               self.board[ni][nj] == player_id and (ni, nj) not in visited:
                if self._dfs_connection(ni, nj, player_id, visited, is_horizontal):
                    return True
        
        return False
    
    def _get_neighbors(self, i, j):
        neighbors = []
        
        neighbors.append((i, j - 1))
        neighbors.append((i, j + 1))
        neighbors.append((i - 1, j))
        neighbors.append((i + 1, j))
        
        if i % 2 == 0:
            neighbors.append((i - 1, j + 1))
            neighbors.append((i + 1, j + 1))
        else:
            neighbors.append((i - 1, j - 1))
            neighbors.append((i + 1, j - 1)) 
        
        return neighbors
    
    def print_board(self):
        """Imprime el tablero en la consola."""
        RED = '\033[91m'
        BLUE = '\033[94m'
        RESET = '\033[0m'
        
        print("\n  ", end="")
        for j in range(self.size):
            print(f"{j} ", end="")
        print()
        
        for i in range(self.size):
            print(" " * i, end="")
            print(f"{i} ", end="")
            
            for j in range(self.size):
                if self.board[i][j] == 0:
                    print(". ", end="")
                elif self.board[i][j] == 1:
                    print(f"{RED}X {RESET}", end="")
                else:
                    print(f"{BLUE}O {RESET}", end="")
            print()
        print()
