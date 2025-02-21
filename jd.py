import sys
import time
import random
import copy

# Max time for iterative deepening search
TIME_LIMIT = 2.0

# Global constants for storing game background

# A dictionary with all valid location names of positions on the board (used for populating game board)
VALID_SPACES = [
    "a1", "d1", "g1",     
    "b2", "d2", "f2", 
    "c3", "d3", "e3",     
    "a4", "b4", "c4", "e4", "f4", "g4",  
    "c5", "d5", "e5",    
    "b6", "d6", "f6",    
    "a7", "d7", "g7"     
]

# Dictionary of each position and the positions that are adjacent to it
ADJACENCY = {
    "a1": ["d1", "a4"],
    "d1": ["a1", "g1", "d2"],
    "g1": ["d1", "g4"],
    "b2": ["d2", "b4"],
    "d2": ["b2", "f2", "d1", "d3"],
    "f2": ["d2", "f4"],
    "c3": ["d3", "c4"],
    "d3": ["c3", "e3", "d2"],
    "e3": ["d3", "e4"],
    "a4": ["a1", "a7", "b4"],
    "b4": ["a4", "c4", "b2", "b6"],
    "c4": ["b4", "c3", "c5"],
    "g4": ["g1", "g7", "f4"],
    "f4": ["g4", "f2", "f6", "e4"],
    "e4": ["e3", "f4", "e5"],
    "a7": ["a4", "d7"],
    "d7": ["a7", "g7", "d6"],
    "g7": ["d7", "g4"],
    "b6": ["b4", "d6"],
    "d6": ["b6", "f6", "d7", "d5"],
    "f6": ["d6", "f4"],
    "c5": ["c4", "d5"],
    "d5": ["c5", "e5", "d6"],
    "e5": ["d5", "e4"]
}

# Every possible mill combination
MILLS = [
    ["a1", "d1", "g1"],
    ["a7", "d7", "g7"],
    ["b2", "d2", "f2"],
    ["b6", "d6", "f6"],
    ["c3", "d3", "e3"],
    ["c5", "d5", "e5"],
    ["a1", "a4", "a7"],
    ["g1", "g4", "g7"],
    ["b2", "b4", "b6"],
    ["f2", "f4", "f6"],
    ["c3", "c4", "c5"],
    ["e3", "e4", "e5"],
    ["d1", "d2", "d3"],
    ["d5", "d6", "d7"],
    ["a4", "b4", "c4"],
    ["e4", "f4", "g4"]
]

# Flag for immediate mode evaluation (possible mills on next move)
IMMEDIATE_MODE = False


# USED FOR DEBUGGING TO SEPARATE TEXT FILE TO NOT CONFUSE REFEREE WITH STDOUT
# def log_debug(message):
#     with open("debug.txt", "a") as f:
#         f.write(message + "\n")


#* @brief Initialize the base state of the game, with an empty board and full hands
#*
#* @return Initial state of the game
def initial_state():
    state = {
        "board": {pos: None for pos in VALID_SPACES},
        "hand": {"blue": 10, "orange": 10},
        "mill_counter": 0, # Used to count to 20 for stalemate
        "turn": None  
    }
    return state


#* @brief Checks if the move will form a mill
#*
#* @param board current state of the board
#* @param pos position of the move
#* @param color color of the player
#*
#* @return boolean value indicating if the move forms a mill
def forms_mill(board, pos, color):
    for mill in MILLS:
        if pos in mill:
            if all(board[p] == color or p == pos for p in mill):
                if all((p == pos) or (board[p] == color) for p in mill):
                    return True
    return False


#* @brief Checks if a move will block an opponent's mill
#*
#* @param board current state of the board
#* @param pos position of the move
#* @param opp_color color of the opponent
#*
#* @return boolean value indicating if the move blocks the opponent's mill
def blocks_mill(board, pos, opp_color):
    for mill in MILLS:
        if pos in mill:
            # Exclude the position 'pos' where we just played.
            other_positions = [p for p in mill if p != pos]
            # Since each mill is three positions, there will be exactly two others.
            if len(other_positions) == 2 and all(board[p] == opp_color for p in other_positions):
                return True
    return False


#* @brief Lists all of the opponent's pieces that can be legally removed when player scores a mill
#*
#* @param state current state of the game
#* @param opponent_color color of the opponent
#*
#* @return list of all opponent pieces that can be legally removed
def get_mill_removals(state, opponent_color):
    board = state["board"]
    candidates = [pos for pos, occ in board.items() if occ == opponent_color and not forms_mill(board, pos, opponent_color)]
    if candidates:
        return candidates
    return [pos for pos, occ in board.items() if occ == opponent_color]


#* @brief Creates a deep copy of the given game state to test out moves without affecting the real game
#*
#* @param state current state of the game
#*
#* @return copy of given game state
def copy_state(state):
    return copy.deepcopy(state)


#* @brief Changes the state of the game between player turns
#*
#* @param state current state of the game
#*
#* @return void
def change_turn(state):
    state["turn"] = "blue" if state["turn"] == "orange" else "orange"


#* @brief Counts the number of pieces of a given color on the board, used for determining game win/loss
#*
#* @param state current state of the game
#* @param color color of the player
#*
#* @return number of pieces the player has
def count_board_pieces(state, color):
    return sum(1 for occ in state["board"].values() if occ == color)

#* @brief Generates all possible moves the given player can make
#*
#* @param state current state of the game
#* @param color color of the player
#*
#* @return list of all possible moves that the player can make
def generate_moves(state, color):
    moves = []
    board = state["board"]
    opponent_color = "blue" if color == "orange" else "orange"
    pieces_on_board = count_board_pieces(state, color)
    pieces_in_hand = state["hand"][color]
    
    # Possible moves from hand
    if pieces_in_hand > 0:
        for pos in VALID_SPACES:
            if board[pos] is None:
                new_board = board.copy()
                new_board[pos] = color
                mill_formed = forms_mill(new_board, pos, color)
                if mill_formed:
                    removals = get_mill_removals(state, opponent_color)
                    for rem in removals:
                        moves.append(("h", pos, rem))
                else:
                    moves.append(("h", pos, "r0"))
    
    # Possible moves from adjacent moves
    player_positions = [pos for pos, occ in board.items() if occ == color]
    for src in player_positions:
        if pieces_on_board == 3 and pieces_in_hand == 0:
            possible_dests = [p for p in VALID_SPACES if board[p] is None]
        else:
            possible_dests = [p for p in ADJACENCY[src] if board[p] is None]
        for dest in possible_dests:
            new_board = board.copy()
            new_board[src] = None
            new_board[dest] = color
            mill_formed = forms_mill(new_board, dest, color)
            if mill_formed:
                removals = get_mill_removals(state, opponent_color)
                for rem in removals:
                    moves.append((src, dest, rem))
            else:
                moves.append((src, dest, "r0"))
                
    return moves


#* @brief Applies a given move, and returns the game state after the move is applied
#*
#* @param state current state of the game
#* @param move tuple of the form (source, dest, removal)
#*
#* @return the new state of the game after the move is applied
def apply_move(state, move):
    new_state = copy_state(state)
    board = new_state["board"]
    source, dest, removal = move
    color = state["turn"]
    opponent_color = "blue" if color == "orange" else "orange"
    mill_formed = False

    if source.startswith("h"):
        new_state["hand"][color] -= 1
        board[dest] = color
        if forms_mill(board, dest, color):
            mill_formed = True
    else:
        board[source] = None
        board[dest] = color
        if forms_mill(board, dest, color):
            mill_formed = True

    if mill_formed and removal != "r0":
        board[removal] = None
        new_state["mill_counter"] = 0
    else:
        new_state["mill_counter"] += 1

    new_state["move_played"] = dest

    change_turn(new_state)
    return new_state


#* @brief Checks if the current game state is terminal (no legal moves, a player has less than 3 pieces, or stalemate)
#*
#* @param state current state of the game
#*
#* @return boolean value indicating if the game is over
def is_terminal(state):
    for color in ["blue", "orange"]:
        if count_board_pieces(state, color) + state["hand"][color] < 3:
            return True
    if not generate_moves(state, state["turn"]):
        return True
    if state["mill_counter"] >= 20:
        return True
    return False

#* @brief Uses a series of heuristics to evaluate the value of the current game state
#*
#* @param state current state of the game
#* @param player color of the player
#* @param is_root boolean value to determine if the current state is the root
#*
#* @return the heuristic value of the current game state
def evaluate(state, player, is_root):
    global IMMEDIATE_MODE
    opponent = "blue" if player == "orange" else "orange"
    board = state["board"]
    move_played = state["move_played"]
    score = 0

    if is_terminal(state):
        if count_board_pieces(state, player) + state["hand"][player] < 3 or not generate_moves(state, player):
            return -10000 # we lose the game
        if count_board_pieces(state, opponent) + state["hand"][opponent] < 3 or not generate_moves(state, opponent):
            return 10000 # we win the game
        return 0
    
    if IMMEDIATE_MODE:
        if forms_mill(board, move_played, player):
            score += 5000 # we form a mill on our next turn
        
        if blocks_mill(board, move_played, opponent):
            score += 3000 # we block a mill on our next turn

    my_pieces_left = count_board_pieces(state, player) + state["hand"][player]
    opp_pieces_left = count_board_pieces(state, opponent) + state["hand"][opponent]
    score += 100 * (my_pieces_left - opp_pieces_left) # our number of pieces left vs opponent's number of pieces left

    my_moves = len(generate_moves(state, player))
    opp_moves = len(generate_moves(state, opponent))
    score += 10 * (my_moves - opp_moves) # our possible moves vs opponent's possible moves

    strategic_positions = {"d2", "d6", "b4", "f4"}
    my_control = sum(1 for pos in strategic_positions if board.get(pos) == player)
    opp_control = sum(1 for pos in strategic_positions if board.get(pos) == opponent)
    score += 20 * (my_control - opp_control) # we hold strategic positions on the board vs opponent holds strategic positions on the board

    return score


#* @brief Minimax algorithm using alpha-beta pruning to find the best move at a given depth
#*
#* @param state current state of the game
#* @param depth depth of the search tree
#* @param alpha alpha value for pruning
#* @param beta beta value for pruning
#* @param maximizing_player boolean value to determine if the player is maximizing
#* @param player color of the player
#* @param start_time time the search started
#* @param is_root boolean value to determine if the current state is the root
#*
#* @return the value of the best move found by the algorithm and the move itself
def alphabeta(state, depth, alpha, beta, maximizing_player, player, start_time, is_root=False):
    if time.time() - start_time > TIME_LIMIT * 0.95: # save 5% of our move time for final calculations
        return evaluate(state, player, is_root), None

    if depth == 0 or is_terminal(state):
        return evaluate(state, player, is_root), None

    if is_root:
        legal_moves = generate_moves(state, player)
    else:
        legal_moves = generate_moves(state, state["turn"])

    best_move = None

    if maximizing_player:
        value = -float('inf')
        for move in legal_moves:
            child = apply_move(state, move)
            child_value, _ = alphabeta(child, depth - 1, alpha, beta, False, player, start_time)
            if child_value > value:
                value = child_value
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cutoff.
        return value, best_move
    else: # minimizing player
        value = float('inf')
        for move in legal_moves:
            child = apply_move(state, move)
            child_value, _ = alphabeta(child, depth - 1, alpha, beta, True, player, start_time)
            if child_value < value:
                value = child_value
                best_move = move
            beta = min(beta, value)
            if beta <= alpha:
                break  # Alpha cutoff.
        return value, best_move

#* @brief Continuously runs the minimax algorithm with alpha-beta pruning at iterating depths until time is up
#*
#* @param state current state of the game
#* @param player color of the player
#*
#* @return the best move found by the algorithm
def iterative_deepening(state, player):
    global IMMEDIATE_MODE
    IMMEDIATE_MODE = True # global variable to track whether we are searching the immediate next move (to check for possible mills/mill blocks)
    start_time = time.time()
    best_move = None
    depth = 1
    while True:
        if time.time() - start_time > TIME_LIMIT * 0.9:
            break
        value, move = alphabeta(state, depth, -float('inf'), float('inf'), True, player, start_time, is_root=True)
        if time.time() - start_time > TIME_LIMIT * 0.9:
            break
        if move is not None:
            best_move = move
        depth += 1
        IMMEDIATE_MODE = False
    return best_move


#* @brief Converts a move from string form to tuple form
#*
#* @param string representation of the move
#* @param player_color color of the player
#*
#* @return tuple of the move in the form (source, dest, removal)
def parse_move(move_str):
    parts = move_str.strip().split()
    if len(parts) != 3:
        raise ValueError("Invalid move format")
    return tuple(parts) 


#* @brief Converts a move from tuple form to string form
#*
#* @param move tuple of the form (source, dest, removal)
#* @param player_color color of the player
#*
#* @return string representation of the move
def move_to_string(move, player_color):
    source, dest, removal = move
    if source == "h":
        source = "h1" if player_color == "blue" else "h2"
    return f"{source} {dest} {removal}"

def main():
    # Read initial color
    player_color = input().strip().lower()
    
    state = initial_state()
    state["turn"] = "blue" 
    
    # Blue makes the first move
    if player_color == "blue":
        move = iterative_deepening(state, player_color)
        if move is None:
            sys.exit("No valid move found")
        state = apply_move(state, move)

        print(move_to_string(move, player_color), flush=True)
    
    # Main loop
    while True:
        try:
            game_input = input().strip()
            if game_input.startswith("END"):
                break

            opp_move = parse_move(game_input)
            state = apply_move(state, opp_move)

            if is_terminal(state):
                break

            move = iterative_deepening(state, player_color)
            if move is None:
                break
            state = apply_move(state, move)
            print(move_to_string(move, player_color), flush=True)

            if is_terminal(state):
                break

        except EOFError:
            break

if __name__ == "__main__":
    main()