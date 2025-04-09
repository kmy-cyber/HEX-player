from player import HexPlayer
from board import HexBoard
import random
import time
import os


def play_game(player1, player2, board_size=11, max_moves=1000, print_moves=True):
    board = HexBoard(board_size)
    players = [player1, player2]
    current_player_idx = 0
    
    move_count = 0
    
    if print_moves:
        print(f"Starting a new game: Player 1 (X) vs Player 2 (O)")
        board.print_board()
    
    while move_count < max_moves:
        current_player = players[current_player_idx]
        player_id = current_player.player_id
        
        start_time = time.time()
        move = current_player.play(board)
        end_time = time.time()
        
        if move not in board.get_possible_moves():
            print(f"Player {player_id} made an invalid move: {move}")
            return 3 - player_id
        
        board.place_piece(move[0], move[1], player_id)
        move_count += 1
        
        if print_moves:
            print(f"Player {player_id} places at {move} (took {end_time - start_time:.2f}s)")
            board.print_board()
        
        if board.check_connection(player_id):
            if print_moves:
                print(f"Player {player_id} wins in {move_count} moves!")
            return player_id
        
        current_player_idx = 1 - current_player_idx
    
    if print_moves:
        print(f"Game ended in a draw after {move_count} moves.")
    return 0


def run_tournament(player1_class, player2_class, board_size=11, num_games=10):
    player1_wins = 0
    player2_wins = 0
    draws = 0
    
    print(f"Starting tournament: {player1_class.__name__} vs {player2_class.__name__}")
    print(f"Board size: {board_size}x{board_size}, Number of games: {num_games}")
    
    for game_num in range(num_games):
        print(f"\nGame {game_num + 1}/{num_games}")
        
        # Alternate who goes first
        if game_num % 2 == 0:
            player1 = player1_class(1)
            player2 = player2_class(2)
            print(f"{player1_class.__name__} (1) vs {player2_class.__name__} (2)")
        else:
            player1 = player2_class(1)
            player2 = player1_class(2)
            print(f"{player2_class.__name__} (1) vs {player1_class.__name__} (2)")
        
        # Play the game
        winner = play_game(player1, player2, board_size, print_moves=True)
        
        # Record the result
        if winner == 0:
            draws += 1
            print("Game ended in a draw")
        elif (game_num % 2 == 0 and winner == 1) or (game_num % 2 == 1 and winner == 2):
            player1_wins += 1
            print(f"{player1_class.__name__} wins!")
        else:
            player2_wins += 1
            print(f"{player2_class.__name__} wins!")
    
    print("\nTournament Results:")
    print(f"{player1_class.__name__}: {player1_wins} wins")
    print(f"{player2_class.__name__}: {player2_wins} wins")
    print(f"Draws: {draws}")
    
    return (player1_wins, player2_wins, draws)


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    
    class RandomPlayer(HexPlayer):
        def play(self, board):
            possible_moves = board.get_possible_moves()
            return random.choice(possible_moves)
    
    player1_class = HexPlayer
    # player2_class = RandomPlayer
    player2_class = HexPlayer
    
    board_size = 11
    num_games = 2
    
    run_tournament(player1_class, player2_class, board_size, num_games)
