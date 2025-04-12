import time
import copy
import random

class Player:
    def __init__(self, player_id: int):
        # Inicializa un jugador con su ID
        self.player_id = player_id

    def play(self, board):
        # Método que debe ser implementado por las subclases para realizar un movimiento
        raise NotImplementedError("¡Implementa este método!")


class HexBoard:
    def __init__(self, size: int):
        # Inicializa un tablero de Hex con el tamaño especificado
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]

    def clone(self):
        # Crea una copia del tablero actual
        pass

    def place_piece(self, row: int, col: int, player_id: int) -> bool:
        # Coloca una pieza del jugador en la posición especificada
        pass

    def get_possible_moves(self) -> list:
        # Obtiene una lista de todos los movimientos posibles
        pass
    
    def check_connection(self, player_id: int) -> bool:
        # Verifica si el jugador ha creado una conexión ganadora
        pass

class HexPlayer(Player):
    def __init__(self, player_id: int, max_time: int=10):
        # Inicializa un jugador de Hex con su ID y tiempo máximo de juego
        super().__init__(player_id)
        self.opponent_id = 3 - player_id
        self.max_depth = 5
        self.max_time = max_time
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
        self.start_time = 0
        self.use_symmetry = True
        self.first_move = None
        self.opening_book = {
            11: [(5, 5), (4, 5), (5, 4), (6, 5), (5, 6)],
            8: [(3, 3), (4, 3), (3, 4)],
            7: [(3, 3)],
            6: [(2, 2)],
        }

    def play(self, board: HexBoard):
        # Determina el mejor movimiento para el jugador en el tablero actual
        self.start_time = time.time()
        
        empty_cells = sum(row.count(0) for row in board.board)
        if empty_cells == board.size * board.size:
            if board.size in self.opening_book:
                return random.choice(self.opening_book[board.size])
        
        if self.use_symmetry:
            if empty_cells == board.size * board.size - 1:
                for r in range(board.size):
                    for c in range(board.size):
                        if board.board[r][c] != 0:
                            self.first_move = (r, c)
                            if r == board.size // 2 and c == board.size // 2:
                                return (r, c+1)
                            if board.size % 2 == 1 and board.board[board.size//2][board.size//2] == 0:
                                return (board.size//2, board.size//2)
                            else:
                                return (c, r)
            
            if self.first_move is not None:
                last_move = None
                for r in range(board.size):
                    for c in range(board.size):
                        if board.board[r][c] == self.opponent_id and all(
                            board.board[nr][nc] != self.opponent_id 
                            for nr, nc in self._get_neighbors(r, c) 
                            if 0 <= nr < board.size and 0 <= nc < board.size
                        ):
                            last_move = (r, c)
                            break
                    if last_move:
                        break
                
                if last_move:
                    sym_move = (last_move[1], last_move[0])
                    if 0 <= sym_move[0] < board.size and 0 <= sym_move[1] < board.size and board.board[sym_move[0]][sym_move[1]] == 0:
                        return sym_move
        
        candidate_moves = self.generate_candidate_moves(board)
        
        if not candidate_moves:
            candidate_moves = board.get_possible_moves()
        
        if len(candidate_moves) == 1:
            return candidate_moves[0]
        
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        for move in candidate_moves:
            new_board = board.clone()
            new_board.place_piece(move[0], move[1], self.player_id)
            
            score = self.minimax(new_board, self.max_depth - 1, alpha, beta, False)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
            
            if time.time() - self.start_time > self.max_time * 0.9:
                break
        
        if best_move is None:
            return random.choice(board.get_possible_moves())
            
        return best_move

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        # Implementa el algoritmo minimax con poda alfa-beta para evaluar movimientos
        if board.check_connection(self.player_id):
            return 1000
        
        if board.check_connection(self.opponent_id):
            return -1000
        
        if depth == 0 or time.time() - self.start_time > self.max_time * 0.9:
            return self.evaluate_board(board)
        
        candidate_moves = self.generate_candidate_moves(board)
        
        if not candidate_moves:
            candidate_moves = board.get_possible_moves()
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in candidate_moves:
                new_board = board.clone()
                new_board.place_piece(move[0], move[1], self.player_id)
                
                eval = self.minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
                
                if time.time() - self.start_time > self.max_time * 0.9:
                    break
                    
            return max_eval
        else:
            min_eval = float('inf')
            for move in candidate_moves:
                new_board = board.clone()
                new_board.place_piece(move[0], move[1], self.opponent_id)
                
                eval = self.minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                
                if time.time() - self.start_time > self.max_time * 0.9:
                    break
                    
            return min_eval

    def evaluate_board(self, board):
        # Evalúa la posición actual del tablero para determinar qué tan favorable es
        player_groups = self.identify_groups(board, self.player_id)
        opponent_groups = self.identify_groups(board, self.opponent_id)
        
        player_influence = self.calculate_influence_region(board, player_groups, self.player_id)
        opponent_influence = self.calculate_influence_region(board, opponent_groups, self.opponent_id)
        
        player_connectivity = self.calculate_connectivity(board, player_groups, self.player_id)
        opponent_connectivity = self.calculate_connectivity(board, opponent_groups, self.opponent_id)
        
        player_potential = self.calculate_winning_potential(board, player_groups, self.player_id)
        opponent_potential = self.calculate_winning_potential(board, opponent_groups, self.opponent_id)
        
        score = (
            len(player_influence) - len(opponent_influence) +
            player_connectivity - opponent_connectivity +
            player_potential - opponent_potential
        )
        
        return score

    def identify_groups(self, board, player_id):
        # Identifica grupos conectados de piezas del mismo jugador
        groups = []
        visited = set()
        
        for r in range(board.size):
            for c in range(board.size):
                if board.board[r][c] == player_id and (r, c) not in visited:
                    group = []
                    self.dfs_group(board, r, c, player_id, visited, group)
                    groups.append(group)
        
        return groups

    def dfs_group(self, board, r, c, player_id, visited, group):
        # Realiza una búsqueda en profundidad para encontrar piezas conectadas
        if (r, c) in visited or r < 0 or r >= board.size or c < 0 or c >= board.size or board.board[r][c] != player_id:
            return
        
        visited.add((r, c))
        group.append((r, c))
        
        for dr, dc in self.directions:
            nr, nc = r + dr, c + dc
            self.dfs_group(board, nr, nc, player_id, visited, group)

    def calculate_influence_region(self, board, groups, player_id):
        # Calcula la región de influencia de un jugador en el tablero
        influence = set()
        
        for group in groups:
            for pos in group:
                influence.add(pos)
        
        for group in groups:
            for r, c in group:
                for dr, dc in self.directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < board.size and 0 <= nc < board.size and board.board[nr][nc] == 0:
                        influence.add((nr, nc))
        
        return influence

    def calculate_connectivity(self, board, groups, player_id):
        # Calcula la conectividad de los grupos de un jugador con los bordes del tablero
        connectivity = 0
        
        if player_id == 2:
            for group in groups:
                top_connected = any(pos[0] == 0 for pos in group)
                bottom_connected = any(pos[0] == board.size - 1 for pos in group)
                
                if top_connected and bottom_connected:
                    connectivity += 500
                elif top_connected:
                    connectivity += 10
                elif bottom_connected:
                    connectivity += 10
                
                connectivity += len(group)
        
        else:
            for group in groups:
                left_connected = any(pos[1] == 0 for pos in group)
                right_connected = any(pos[1] == board.size - 1 for pos in group)
                
                if left_connected and right_connected:
                    connectivity += 500
                elif left_connected:
                    connectivity += 10
                elif right_connected:
                    connectivity += 10
                
                connectivity += len(group)
        
        return connectivity

    def calculate_winning_potential(self, board, groups, player_id):
        # Evalúa el potencial de victoria basado en la longitud de los caminos más cortos
        potential = 0
        
        if player_id == 2:
            for c in range(board.size):
                path_length = self.shortest_path_length(board, 0, c, board.size - 1, None, player_id)
                if path_length > 0:
                    potential += (board.size * 2 - path_length)
        
        else:
            for r in range(board.size):
                path_length = self.shortest_path_length(board, r, 0, None, board.size - 1, player_id)
                if path_length > 0:
                    potential += (board.size * 2 - path_length)
        
        return potential

    def shortest_path_length(self, board, start_r, start_c, target_r, target_c, player_id):
        # Encuentra la longitud del camino más corto entre dos puntos
        import heapq
        
        queue = [(0, start_r, start_c)]
        visited = set()
        
        while queue:
            dist, r, c = heapq.heappop(queue)
            
            if (r, c) in visited:
                continue
            
            visited.add((r, c))
            
            if (target_r is not None and r == target_r and 
                target_c is not None and c == target_c):
                return dist
            elif target_r is not None and r == target_r and target_c is None:
                return dist
            elif target_r is None and target_c is not None and c == target_c:
                return dist
            
            for dr, dc in self.directions:
                nr, nc = r + dr, c + dc
                
                if 0 <= nr < board.size and 0 <= nc < board.size and (nr, nc) not in visited:
                    if board.board[nr][nc] == player_id:
                        cost = 0
                    elif board.board[nr][nc] == 0:
                        cost = 1
                    else:
                        continue
                    
                    heapq.heappush(queue, (dist + cost, nr, nc))
        
        return -1

    def find_carriers(self, board, group, player_id):
        # Encuentra casillas vacías adyacentes a un grupo que pueden extender la conexión
        carriers = set()
        
        for r, c in group:
            for dr, dc in self.directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < board.size and 0 <= nc < board.size and board.board[nr][nc] == 0:
                    carriers.add((nr, nc))
        
        return carriers

    def generate_candidate_moves(self, board):
        # Genera una lista de movimientos candidatos basados en la estrategia
        candidates = set()
        
        player_groups = self.identify_groups(board, self.player_id)
        opponent_groups = self.identify_groups(board, self.opponent_id)
        
        player_topbottom = self.find_topbottom_groups(board, player_groups, self.player_id)
        opponent_leftright = self.find_leftright_groups(board, opponent_groups, self.opponent_id)
        
        for group in player_topbottom:
            carriers = self.find_carriers(board, group, self.player_id)
            candidates.update(carriers)
        
        for group in opponent_leftright:
            carriers = self.find_carriers(board, group, self.opponent_id)
            candidates.update(carriers)
        
        if self.player_id == 1:
            opponent_top_groups = self.find_top_groups(board, opponent_groups, self.opponent_id)
            opponent_bottom_groups = self.find_bottom_groups(board, opponent_groups, self.opponent_id)
            
            for group in opponent_top_groups:
                blocking_moves = self.find_one_to_connect(board, group, self.opponent_id, "bottom")
                candidates.update(blocking_moves)
            
            for group in opponent_bottom_groups:
                blocking_moves = self.find_one_to_connect(board, group, self.opponent_id, "top")
                candidates.update(blocking_moves)
        else:
            opponent_left_groups = self.find_left_groups(board, opponent_groups, self.opponent_id)
            opponent_right_groups = self.find_right_groups(board, opponent_groups, self.opponent_id)
            
            for group in opponent_left_groups:
                blocking_moves = self.find_one_to_connect(board, group, self.opponent_id, "right")
                candidates.update(blocking_moves)
            
            for group in opponent_right_groups:
                blocking_moves = self.find_one_to_connect(board, group, self.opponent_id, "left")
                candidates.update(blocking_moves)
        
        for group1 in opponent_groups:
            for group2 in opponent_groups:
                if group1 != group2:
                    blocking_moves = self.find_connecting_moves(board, group1, group2, self.opponent_id)
                    candidates.update(blocking_moves)
        
        virtual_connections = self.find_virtual_connections(board, opponent_groups, self.opponent_id)
        candidates.update(virtual_connections)
        
        top_groups = self.find_top_groups(board, player_groups, self.player_id)
        bottom_groups = self.find_bottom_groups(board, player_groups, self.player_id)
        
        for group in top_groups:
            one_to_connect = self.find_one_to_connect(board, group, self.player_id, "bottom")
            candidates.update(one_to_connect)
        
        for group in bottom_groups:
            one_to_connect = self.find_one_to_connect(board, group, self.player_id, "top")
            candidates.update(one_to_connect)
        
        for top_group in top_groups:
            for bottom_group in bottom_groups:
                connecting_moves = self.find_connecting_moves(board, top_group, bottom_group, self.player_id)
                candidates.update(connecting_moves)
        
        if candidates:
            return list(candidates)
        
        near_existing = set()
        for r in range(board.size):
            for c in range(board.size):
                if board.board[r][c] == self.player_id:
                    for dr, dc in self.directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < board.size and 0 <= nc < board.size and board.board[nr][nc] == 0:
                            near_existing.add((nr, nc))
        
        if near_existing:
            return list(near_existing)
        
        return board.get_possible_moves()

    def find_topbottom_groups(self, board, groups, player_id):
        # Encuentra grupos que conectan los bordes superior e inferior
        topbottom_groups = []
        
        for group in groups:
            top_connected = any(pos[0] == 0 for pos in group)
            bottom_connected = any(pos[0] == board.size - 1 for pos in group)
            
            if top_connected and bottom_connected:
                topbottom_groups.append(group)
        
        return topbottom_groups

    def find_leftright_groups(self, board, groups, player_id):
        # Encuentra grupos que conectan los bordes izquierdo y derecho
        leftright_groups = []
        
        for group in groups:
            left_connected = any(pos[1] == 0 for pos in group)
            right_connected = any(pos[1] == board.size - 1 for pos in group)
            
            if left_connected and right_connected:
                leftright_groups.append(group)
        
        return leftright_groups

    def find_left_groups(self, board, groups, player_id):
        # Encuentra grupos conectados al borde izquierdo
        left_groups = []
        
        for group in groups:
            if any(pos[1] == 0 for pos in group):
                left_groups.append(group)
        
        return left_groups

    def find_right_groups(self, board, groups, player_id):
        # Encuentra grupos conectados al borde derecho
        right_groups = []
        
        for group in groups:
            if any(pos[1] == board.size - 1 for pos in group):
                right_groups.append(group)
        
        return right_groups

    def find_top_groups(self, board, groups, player_id):
        # Encuentra grupos conectados al borde superior
        top_groups = []
        
        for group in groups:
            if any(pos[0] == 0 for pos in group):
                top_groups.append(group)
        
        return top_groups

    def find_bottom_groups(self, board, groups, player_id):
        # Encuentra grupos conectados al borde inferior
        bottom_groups = []
        
        for group in groups:
            if any(pos[0] == board.size - 1 for pos in group):
                bottom_groups.append(group)
        
        return bottom_groups

    def is_connected_to_left(self, board, r, c, player_id):
        # Verifica si una posición está conectada al borde izquierdo
        visited = set()
        return self._is_connected_to_edge(board, r, c, player_id, visited, lambda pos: pos[1] == 0)

    def is_connected_to_right(self, board, r, c, player_id):
        # Verifica si una posición está conectada al borde derecho
        visited = set()
        return self._is_connected_to_edge(board, r, c, player_id, visited, lambda pos: pos[1] == board.size - 1)

    def find_virtual_connections(self, board, groups, player_id):
        # Encuentra conexiones virtuales entre grupos
        virtual_connections = set()
        
        for group in groups:
            for r, c in group:
                for dr1, dc1 in self.directions:
                    nr1, nc1 = r + dr1, c + dc1
                    if 0 <= nr1 < board.size and 0 <= nc1 < board.size and board.board[nr1][nc1] == 0:
                        for dr2, dc2 in self.directions:
                            nr2, nc2 = nr1 + dr2, nc1 + dc2
                            if 0 <= nr2 < board.size and 0 <= nc2 < board.size and board.board[nr2][nc2] == 0:
                                test_board = board.clone()
                                test_board.place_piece(nr1, nc1, player_id)
                                test_board.place_piece(nr2, nc2, player_id)
                                
                                new_groups = self.identify_groups(test_board, player_id)
                                if len(new_groups) < len(groups):
                                    virtual_connections.add((nr1, nc1))
                                    virtual_connections.add((nr2, nc2))
        
        for group in groups:
            for r, c in group:
                for i in range(4):
                    if i == 0:
                        nr1, nc1 = r - 1, c - 1
                        nr2, nc2 = r + 1, c + 1
                    elif i == 1:
                        nr1, nc1 = r - 1, c + 1
                        nr2, nc2 = r + 1, c - 1
                    elif i == 2:
                        nr1, nc1 = r, c - 1
                        nr2, nc2 = r, c + 1
                    else:
                        nr1, nc1 = r - 1, c
                        nr2, nc2 = r + 1, c
                    
                    if (0 <= nr1 < board.size and 0 <= nc1 < board.size and 
                        0 <= nr2 < board.size and 0 <= nc2 < board.size and
                        board.board[nr1][nc1] == 0 and board.board[nr2][nc2] == 0):
                        
                        for pos in [(nr1, nc1), (nr2, nc2)]:
                            test_board = board.clone()
                            test_board.place_piece(pos[0], pos[1], player_id)
                            
                            if self.creates_strong_connection(test_board, pos, player_id, groups):
                                virtual_connections.add(pos)
        
        return virtual_connections

    def creates_strong_connection(self, board, pos, player_id, original_groups):
        # Determina si un movimiento crea una conexión fuerte entre grupos
        new_groups = self.identify_groups(board, player_id)
        
        if len(new_groups) < len(original_groups):
            return True
        
        connected_to_groups = 0
        r, c = pos
        for dr, dc in self.directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < board.size and 0 <= nc < board.size and board.board[nr][nc] == player_id:
                for i, group in enumerate(original_groups):
                    if any(pos == (nr, nc) for pos in group):
                        connected_to_groups += 1
                        break
        
        return connected_to_groups >= 2

    def is_connected_to_top(self, board, r, c, player_id):
        # Verifica si una posición está conectada al borde superior
        visited = set()
        return self._is_connected_to_edge(board, r, c, player_id, visited, lambda pos: pos[0] == 0)

    def is_connected_to_bottom(self, board, r, c, player_id):
        # Verifica si una posición está conectada al borde inferior
        visited = set()
        return self._is_connected_to_edge(board, r, c, player_id, visited, lambda pos: pos[0] == board.size - 1)

    def _is_connected_to_edge(self, board, r, c, player_id, visited, edge_condition):
        # Función auxiliar para verificar conexiones con los bordes
        if (r, c) in visited:
            return False
        
        if board.board[r][c] != player_id:
            return False
        
        if edge_condition((r, c)):
            return True
        
        visited.add((r, c))
        
        for dr, dc in self.directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < board.size and 0 <= nc < board.size:
                if self._is_connected_to_edge(board, nr, nc, player_id, visited, edge_condition):
                    return True
        
        return False

    def find_connecting_moves(self, board, group1, group2, player_id):
        # Encuentra movimientos que pueden conectar dos grupos
        connecting_moves = set()
        
        adjacent1 = set()
        for r, c in group1:
            for dr, dc in self.directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < board.size and 0 <= nc < board.size and board.board[nr][nc] == 0:
                    adjacent1.add((nr, nc))
        
        adjacent2 = set()
        for r, c in group2:
            for dr, dc in self.directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < board.size and 0 <= nc < board.size and board.board[nr][nc] == 0:
                    adjacent2.add((nr, nc))
        
        common_adjacent = adjacent1.intersection(adjacent2)
        connecting_moves.update(common_adjacent)
        
        for pos1 in adjacent1:
            for pos2 in adjacent2:
                if self.are_adjacent(pos1, pos2):
                    connecting_moves.add(pos1)
                    connecting_moves.add(pos2)
        
        return connecting_moves

    def are_adjacent(self, pos1, pos2):
        # Verifica si dos posiciones son adyacentes
        r1, c1 = pos1
        r2, c2 = pos2
        
        for dr, dc in self.directions:
            if r1 + dr == r2 and c1 + dc == c2:
                return True
        
        return False

    def _get_neighbors(self, r, c):
        # Obtiene las posiciones vecinas de una celda
        neighbors = []
        for dr, dc in self.directions:
            neighbors.append((r + dr, c + dc))
        return neighbors

    def find_one_to_connect(self, board, group, player_id, target):
        # Encuentra movimientos que conectan un grupo a un borde específico
        one_to_connect = set()
        
        temp_board = board.clone()
        
        for r, c in group:
            temp_board.board[r][c] = player_id
        
        adjacent_empty = set()
        for r, c in group:
            for dr, dc in self.directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < board.size and 0 <= nc < board.size and board.board[nr][nc] == 0:
                    adjacent_empty.add((nr, nc))
        
        for r, c in adjacent_empty:
            test_board = temp_board.clone()
            test_board.place_piece(r, c, player_id)
            
            if target == "top" and self.is_connected_to_top(test_board, r, c, player_id):
                one_to_connect.add((r, c))
            elif target == "bottom" and self.is_connected_to_bottom(test_board, r, c, player_id):
                one_to_connect.add((r, c))
            elif target == "left" and self.is_connected_to_left(test_board, r, c, player_id):
                one_to_connect.add((r, c))
            elif target == "right" and self.is_connected_to_right(test_board, r, c, player_id):
                one_to_connect.add((r, c))
        
        return one_to_connect
