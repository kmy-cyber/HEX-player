from base import Player
import numpy as np
from collections import deque
import heapq


class HexPlayer(Player):
    def __init__(self, player_id: int):
        super().__init__(player_id)
        self.opponent_id = 3 - player_id
        self.max_depth = 5
        # posibles direcciones de movimiento
        self.directions = np.array([(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)])
        # Los vecinos en caché para no tener que recalcularlos cada vez :\
        self.neighbors_cache = {}
        # Ayudar a recordar los tipos de cadenas que ya hemos clasificado
        self.chain_type_cache = {}

    def play(self, board):
        possible_moves = board.get_possible_moves()
        size = board.size
        
        # Primer movimiento, tomar el centro - suele ser un buen punto de partida
        if len(possible_moves) == size * size:
            return (size // 2, size // 2)
        
        # Si ser segundos y el centro está ocupado, jugar cerca de él
        if len(possible_moves) == size * size - 1:
            center = (size // 2, size // 2)
            if board.board[center[0]][center[1]] != 0:
                neighbors = self.get_neighbors(center[0], center[1], size)
                for neighbor in neighbors:
                    if board.board[neighbor[0]][neighbor[1]] == 0:
                        return neighbor

        np_board = np.array(board.board)
        
        # Ajustar profundidad en dependencia del estado progreso del juego
        if len(possible_moves) > (size * size) * 0.7:
            self.max_depth = 5
        else:
            self.max_depth = 3

        # ver cadenas que tenemos y las que ha contruido el oponente
        player_chains = self.identify_chains_optimized(np_board, self.player_id, size)
        opponent_chains = self.identify_chains_optimized(np_board, self.opponent_id, size)
        
        # Usar heuristicas para encontrar movimientos factibles
        candidate_moves = self.generate_candidate_moves(board, player_chains, opponent_chains)
        
        if not candidate_moves:
            candidate_moves = possible_moves # considerar todos los posibles 
        
        # Checkear si podemos ganar en movimientos inmediatos (Primera prioridad)
        for move in candidate_moves:
            board_copy = board.clone()
            board_copy.place_piece(move[0], move[1], self.player_id)
            if board_copy.check_connection(self.player_id):
                return move
        
        # Bloquear al oponente si está a punto de ganar (Segunda prioridad)
        for move in possible_moves:
            board_copy = board.clone()
            board_copy.place_piece(move[0], move[1], self.opponent_id)
            if board_copy.check_connection(self.opponent_id):
                return move
        
        # minimax y poda alfa-beta
        best_score = float('-inf')
        best_move = candidate_moves[0] if candidate_moves else possible_moves[0]
        
        alpha = float('-inf')
        beta = float('inf')
        
        for move in candidate_moves:
            board_copy = board.clone()
            board_copy.place_piece(move[0], move[1], self.player_id)
            np_board_copy = np.array(board_copy.board)
            
            influence_region = self.calculate_influence_region_optimized(np_board_copy, move, self.player_id, size)
            
            score = self.minimax(board_copy, np_board_copy, self.max_depth - 1, False, alpha, beta, influence_region)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
        
        return best_move
    
    def minimax(self, board, np_board, depth, is_maximizing, alpha, beta, influence_region=None):
        # Terminal conditions
        if board.check_connection(self.player_id):
            return 100000
        if board.check_connection(self.opponent_id):
            return -100000
        if depth == 0:
            return self.evaluate_optimized(np_board, board.size)
        
        possible_moves = board.get_possible_moves()
        size = board.size
        
        if influence_region and not is_maximizing:
            possible_moves = [move for move in possible_moves if move in influence_region]
            if not possible_moves:
                possible_moves = board.get_possible_moves()
        
        if len(possible_moves) > 10:
            player_id = self.player_id if is_maximizing else self.opponent_id
            opponent_id = self.opponent_id if is_maximizing else self.player_id
            player_chains = self.identify_chains_optimized(np_board, player_id, size)
            opponent_chains = self.identify_chains_optimized(np_board, opponent_id, size)
            candidate_moves = self.generate_candidate_moves(board, player_chains, opponent_chains)
            if candidate_moves:
                possible_moves = candidate_moves
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in possible_moves:
                board_copy = board.clone()
                board_copy.place_piece(move[0], move[1], self.player_id)
                np_board_copy = np.array(board_copy.board)
                
                new_influence_region = self.calculate_influence_region_optimized(np_board_copy, move, self.player_id, size)
                
                value = self.minimax(board_copy, np_board_copy, depth - 1, False, alpha, beta, new_influence_region)
                max_eval = max(max_eval, value)
                
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
                    
            return max_eval
        else:
            min_eval = float('inf')
            for move in possible_moves:
                board_copy = board.clone()
                board_copy.place_piece(move[0], move[1], self.opponent_id)
                np_board_copy = np.array(board_copy.board)
                
                new_influence_region = self.calculate_influence_region_optimized(np_board_copy, move, self.opponent_id, size)
                
                value = self.minimax(board_copy, np_board_copy, depth - 1, True, alpha, beta, new_influence_region)
                min_eval = min(min_eval, value)
                
                beta = min(beta, value)
                if beta <= alpha:
                    break
                    
            return min_eval
    
    def evaluate_optimized(self, np_board, size):
        # Condiciones de victoria
        player_chains = self.identify_chains_optimized(np_board, self.player_id, size)
        opponent_chains = self.identify_chains_optimized(np_board, self.opponent_id, size)
        
        for chain, chain_type in player_chains:
            if (self.player_id == 1 and chain_type == "LeftRight") or (self.player_id == 2 and chain_type == "TopBottom"):
                return 100000
        
        for chain, chain_type in opponent_chains:
            if (self.opponent_id == 1 and chain_type == "LeftRight") or (self.opponent_id == 2 and chain_type == "TopBottom"):
                return -100000
        
        player_score = self.evaluate_chains(player_chains, size, self.player_id)
        opponent_score = self.evaluate_chains(opponent_chains, size, self.opponent_id)
        
        player_path_score = self.shortest_path_score_optimized(np_board, self.player_id, size)
        opponent_path_score = self.shortest_path_score_optimized(np_board, self.opponent_id, size)
        
        return (player_score + player_path_score) - (opponent_score + opponent_path_score)
    
    def identify_chains_optimized(self, np_board, player_id, size):

        player_positions = np.argwhere(np_board == player_id)
        visited = set()
        chains = []
        
        for pos in player_positions:
            i, j = pos
            if (i, j) not in visited:
                chain = set()
                self.dfs_chain_optimized(np_board, i, j, player_id, visited, chain, size)
                chains.append(chain)
        
        classified_chains = []
        for chain in chains:
            chain_key = frozenset(chain)
            if chain_key in self.chain_type_cache:
                chain_type = self.chain_type_cache[chain_key]
            else:
                chain_type = self.classify_chain(chain, size, player_id)
                self.chain_type_cache[chain_key] = chain_type
            classified_chains.append((chain, chain_type))
        
        return classified_chains
    
    def dfs_chain_optimized(self, np_board, i, j, player_id, visited, chain, size):
        if (i, j) in visited or np_board[i, j] != player_id:
            return
        
        visited.add((i, j))
        chain.add((i, j))
        
        neighbors = self.get_neighbors(i, j, size)
        for ni, nj in neighbors:
            self.dfs_chain_optimized(np_board, ni, nj, player_id, visited, chain, size)
    
    def get_neighbors(self, i, j, size):

        key = (i, j, size)
        if key in self.neighbors_cache:
            return self.neighbors_cache[key]
        
        neighbors = []
        
        if j > 0:
            neighbors.append((i, j - 1))
        if j < size - 1:
            neighbors.append((i, j + 1))
        if i > 0:
            neighbors.append((i - 1, j))
        if i < size - 1:
            neighbors.append((i + 1, j))
        
        if i % 2 == 0:
            if i > 0 and j < size - 1:
                neighbors.append((i - 1, j + 1))
            if i < size - 1 and j < size - 1:
                neighbors.append((i + 1, j + 1))
        else:
            if i > 0 and j > 0:
                neighbors.append((i - 1, j - 1))
            if i < size - 1 and j > 0:
                neighbors.append((i + 1, j - 1))
        
        valid_neighbors = [(x, y) for (x, y) in neighbors if 0 <= x < size and 0 <= y < size]
        self.neighbors_cache[key] = valid_neighbors
        return valid_neighbors
    
    def calculate_influence_region_optimized(self, np_board, move, player_id, size):
        """Calculate the influence region for a move using BFS"""
        influence_region = set()
        visited = set()
        
        queue = deque([move])
        visited.add(move)
        
        while queue:
            current = queue.popleft()
            influence_region.add(current)
            
            neighbors = self.get_neighbors(current[0], current[1], size)
            for neighbor in neighbors:
                nx, ny = neighbor
                if (nx, ny) not in visited and np_board[nx, ny] == 0:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
                    
                    second_neighbors = self.get_neighbors(nx, ny, size)
                    for sx, sy in second_neighbors:
                        if np_board[sx, sy] == player_id:
                            influence_region.add((nx, ny))
                            break
        
        return influence_region
    
    def shortest_path_score_optimized(self, np_board, player_id, size):
        """Optimized version of shortest path score using numpy"""
        if player_id == 1:
            starts = [(0, j) for j in range(size)]
            ends = [(size-1, j) for j in range(size)]
        else:
            starts = [(i, 0) for i in range(size)]
            ends = [(i, size-1) for i in range(size)]
        
        # Matriz de distancias
        distances = np.full((size, size), np.inf)
        
        # Ddistancias basadas en el estado del tablero
        player_positions = np.argwhere(np_board == player_id)
        empty_positions = np.argwhere(np_board == 0)
        opponent_positions = np.argwhere(np_board == 3 - player_id)
        
        for i, j in player_positions:
            distances[i, j] = 0
        for i, j in empty_positions:
            distances[i, j] = 1
        
        min_distance = np.inf
        
        for start in starts:
            if np_board[start[0], start[1]] == 3 - player_id:
                continue
                
            pq = [(distances[start[0], start[1]], start)]
            visited = set()
            
            while pq:
                dist, current = heapq.heappop(pq)
                
                if current in visited:
                    continue
                    
                visited.add(current)
                
                if current in ends:
                    min_distance = min(min_distance, dist)
                    break

                neighbors = self.get_neighbors(current[0], current[1], size)
                
                for neighbor in neighbors:
                    if neighbor not in visited:
                        new_dist = dist + distances[neighbor[0], neighbor[1]]
                        if new_dist < distances[neighbor[0], neighbor[1]] and dist <= min_distance:
                            distances[neighbor[0], neighbor[1]] = new_dist
                            heapq.heappush(pq, (new_dist, neighbor))
        
        if min_distance == np.inf:
            return 0
        return 10000 - min_distance
    
    # pequeñas optimizaciones
    
    def classify_chain(self, chain, size, player_id):
        # Veamos si la cadena se conecta a los bordes
        top = any(pos[1] == 0 for pos in chain)
        bottom = any(pos[1] == size - 1 for pos in chain)
        left = any(pos[0] == 0 for pos in chain)
        right = any(pos[0] == size - 1 for pos in chain)
        
        if player_id == 1:  # El jugador 1 conecta izquierda-derecha
            if left and right:
                return "LeftRight"  # Winning chain
            elif left:
                return "Left"
            elif right:
                return "Right"
            else:
                return "Middle"
        else:  # El jugador 2 conecta arriba-abajo
            if top and bottom:
                return "TopBottom"
            elif top:
                return "Top"
            elif bottom:
                return "Bottom"
            else:
                return "Middle"
    
    def evaluate_chains(self, chains, size, player_id):
        score = 0
        
        # Check for winning chains
        for chain, chain_type in chains:
            if (player_id == 1 and chain_type == "LeftRight") or (player_id == 2 and chain_type == "TopBottom"):
                return 10000
            
            chain_size = len(chain)
            if chain_type in ["Top", "Bottom", "Left", "Right"]:
                score += chain_size * 10 
            else:
                score += chain_size * 5 
            
            virtual_connections = self.find_virtual_connections(chain, size, player_id)
            score += len(virtual_connections) * 15
            
            if self.is_one_to_connect(chain, chain_type, size, player_id):
                score += 500
        
        return score
    
    def find_virtual_connections(self, chain, size, player_id):
        virtual_connections = []
        chain_list = list(chain)
        
        # Busquemos patrones de puente
        for i in range(len(chain_list)):
            x1, y1 = chain_list[i]
            neighbors = self.get_neighbors(x1, y1, size)
            
            for nx, ny in neighbors:
                if (nx, ny) not in chain and self.count_common_neighbors(chain, (nx, ny), size) >= 2:
                    virtual_connections.append((nx, ny))
        
        return virtual_connections
    
    def count_common_neighbors(self, chain, pos, size):
        x, y = pos
        neighbors = self.get_neighbors(x, y, size)
        return sum(1 for n in neighbors if n in chain)
    
    def is_one_to_connect(self, chain, chain_type, size, player_id):
        if player_id == 1:
            if chain_type == "Left":
                
                for x, y in chain:
                    if x > size - 3: 
                        return True
            elif chain_type == "Right":
                
                for x, y in chain:
                    if x < 2:  
                        return True
        else:
            if chain_type == "Top":
                
                for x, y in chain:
                    if y > size - 3:  
                        return True
            elif chain_type == "Bottom":
                
                for x, y in chain:
                    if y < 2: 
                        return True
        return False
    
    def generate_candidate_moves(self, board, player_chains, opponent_chains):
        size = board.size
        candidate_moves = set()
        
        # Regla 1: Conectar cadenas que están cerca de ganar
        for chain, chain_type in player_chains:
            if self.is_one_to_connect(chain, chain_type, size, self.player_id):
                # Busquemos movimientos que conectarían esta cadena al borde opuesto
                connecting_moves = self.find_connecting_moves(board, chain, chain_type, self.player_id)
                candidate_moves.update(connecting_moves)
        
        # Regla 2: Bloquear las cadenas del oponente que están cerca de ganar
        for chain, chain_type in opponent_chains:
            if self.is_one_to_connect(chain, chain_type, size, self.opponent_id):
                blocking_moves = self.find_connecting_moves(board, chain, chain_type, self.opponent_id)
                candidate_moves.update(blocking_moves)
        
        # Regla 3: Extender cadenas hacia los bordes
        for chain, chain_type in player_chains:
            if chain_type in ["Top", "Bottom", "Left", "Right", "Middle"]:
                extension_moves = self.find_extension_moves(board, chain, chain_type, self.player_id)
                candidate_moves.update(extension_moves)
        
        # Regla 4: Crear conexiones virtuales
        for chain, _ in player_chains:
            virtual_connection_moves = self.find_virtual_connection_moves(board, chain, size)
            candidate_moves.update(virtual_connection_moves)
        
        # Filtremos para asegurarnos de que todos los movimientos son válidos (celdas vacías)
        valid_candidates = []
        for move in candidate_moves:
            if 0 <= move[0] < size and 0 <= move[1] < size and board.board[move[0]][move[1]] == 0:
                valid_candidates.append(move)
        
        return valid_candidates
    
    def find_connecting_moves(self, board, chain, chain_type, player_id):
        size = board.size
        connecting_moves = set()
        
        if player_id == 1: 
            if chain_type == "Left":
                for x, y in chain:
                    neighbors = self.get_neighbors(x, y, size)
                    for nx, ny in neighbors:
                        if board.board[nx][ny] == 0 and nx > x:
                            connecting_moves.add((nx, ny))
            elif chain_type == "Right":
                for x, y in chain:
                    neighbors = self.get_neighbors(x, y, size)
                    for nx, ny in neighbors:
                        if board.board[nx][ny] == 0 and nx < x:
                            connecting_moves.add((nx, ny))
        else: 
            if chain_type == "Top":
                
                for x, y in chain:
                    neighbors = self.get_neighbors(x, y, size)
                    for nx, ny in neighbors:
                        if board.board[nx][ny] == 0 and ny > y:
                            connecting_moves.add((nx, ny))
            elif chain_type == "Bottom":
                
                for x, y in chain:
                    neighbors = self.get_neighbors(x, y, size)
                    for nx, ny in neighbors:
                        if board.board[nx][ny] == 0 and ny < y:
                            connecting_moves.add((nx, ny))
        
        return connecting_moves
    
    def find_extension_moves(self, board, chain, chain_type, player_id):
        size = board.size
        extension_moves = set()
        
        for x, y in chain:
            neighbors = self.get_neighbors(x, y, size)
            for nx, ny in neighbors:
                if board.board[nx][ny] == 0:
                    if player_id == 1:
                        if (chain_type == "Left" and nx > x) or (chain_type == "Right" and nx < x) or chain_type == "Middle":
                            extension_moves.add((nx, ny))
                    else: 
                        if (chain_type == "Top" and ny > y) or (chain_type == "Bottom" and ny < y) or chain_type == "Middle":
                            extension_moves.add((nx, ny))
        
        return extension_moves
    
    def find_virtual_connection_moves(self, board, chain, size):
        virtual_connection_moves = set()
        chain_list = list(chain)
        
        for i in range(len(chain_list)):
            for j in range(i+1, len(chain_list)):
                x1, y1 = chain_list[i]
                x2, y2 = chain_list[j]
                
                if abs(x1 - x2) <= 2 and abs(y1 - y2) <= 2:
                    # Find common empty neighbors
                    neighbors1 = set(self.get_neighbors(x1, y1, size))
                    neighbors2 = set(self.get_neighbors(x2, y2, size))
                    common_neighbors = neighbors1.intersection(neighbors2)
                    
                    for nx, ny in common_neighbors:
                        if board.board[nx][ny] == 0:
                            virtual_connection_moves.add((nx, ny))
        
        return virtual_connection_moves
