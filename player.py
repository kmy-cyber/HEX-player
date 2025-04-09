from base import Player


class HexPlayer(Player):
    def __init__(self, player_id: int):
        super().__init__(player_id)
        self.opponent_id = 3 - player_id
        self.max_depth = 4

    def play(self, board):
        possible_moves = board.get_possible_moves()
        
        if len(possible_moves) == board.size * board.size:
            return (board.size // 2, board.size // 2)
        
        if len(possible_moves) > (board.size * board.size) * 0.7:
            self.max_depth = 3
        else:
            self.max_depth = 2
        
        best_score = float('-inf')
        best_move = possible_moves[0]
        
        alpha = float('-inf')
        beta = float('inf')
        
        for move in possible_moves:
            board_copy = board.clone()
            board_copy.place_piece(move[0], move[1], self.player_id)
            
            if board_copy.check_connection(self.player_id):
                return move
            
            score = self.minimax(board_copy, self.max_depth - 1, False, alpha, beta)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
        
        return best_move
    
    def minimax(self, board, depth, is_maximizing, alpha, beta):
        if depth == 0 or board.check_connection(self.player_id) or board.check_connection(self.opponent_id):
            return self.evaluate(board)
        
        possible_moves = board.get_possible_moves()
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in possible_moves:
                board_copy = board.clone()
                board_copy.place_piece(move[0], move[1], self.player_id)
                
                value = self.minimax(board_copy, depth - 1, False, alpha, beta)
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
                
                value = self.minimax(board_copy, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, value)
                
                beta = min(beta, value)
                if beta <= alpha:
                    break
                    
            return min_eval
    
    def evaluate(self, board):
        if board.check_connection(self.player_id):
            return 100000
        if board.check_connection(self.opponent_id):
            return -100000
        
        player_score = self.shortest_path_score(board, self.player_id)
        opponent_score = self.shortest_path_score(board, self.opponent_id)
        
        return player_score - opponent_score
    
    def shortest_path_score(self, board, player_id):
        import heapq
        
        size = board.size
        
        if player_id == 1:
            starts = [(i, 0) for i in range(size)]
            ends = [(i, size-1) for i in range(size)]
        else:
            starts = [(0, j) for j in range(size)]
            ends = [(size-1, j) for j in range(size)]
        
        distances = {}
        for i in range(size):
            for j in range(size):
                distances[(i, j)] = float('inf')
        
        for i in range(size):
            for j in range(size):
                if board.board[i][j] == player_id:
                    distances[(i, j)] = 0
                elif board.board[i][j] != 0:
                    distances[(i, j)] = float('inf')
                else:
                    distances[(i, j)] = 1
        
        min_distance = float('inf')
        
        for start in starts:
            if board.board[start[0]][start[1]] == 3 - player_id:
                continue
                
            pq = [(distances[start], start)]
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
                        new_dist = dist + distances[neighbor]
                        if new_dist < distances[neighbor] and dist <= min_distance:
                            distances[neighbor] = new_dist
                            heapq.heappush(pq, (new_dist, neighbor))
        
        if min_distance == float('inf'):
            return 0
        return 10000 - min_distance
    
    def get_neighbors(self, i, j, size):
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
        
        return [(x, y) for (x, y) in neighbors if 0 <= x < size and 0 <= y < size]