import sys
import time
import random
import copy

# Max time for iterative deepening search
TIME_LIMIT = 2.0

# Global constants for storing game background

VALID_SPACES = [
    "a1", "d1", "g1",     
    "b2", "d2", "f2", 
    "c3", "d3", "e3",     
    "a4", "b4", "c4", "e4", "f4", "g4",  
    "c5", "d5", "e5",    
    "b6", "d6", "f6",    
    "a7", "d7", "g7"     
]

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

# Debugging to separate file to not confuse referee in stdout
# Change output file name to match your file naming
def log_debug(message):
    with open("aarondebug.txt", "a") as f:
        f.write(message + "\n")



# Initialize the initial state
def initial_state():
    state = {
        "board": {pos: None for pos in VALID_SPACES},
        "hand": {"blue": 10, "orange": 10},
        "mill_counter": 0, # Used to count to 20 for stalemate
        "turn": None  
    }
    return state

# Checks if a mill has been formed by a specific color by playing a certain position
def forms_mill(board, pos, color):
    for mill in MILLS:
        if pos in mill:
            if all(board[p] == color or p == pos for p in mill):
                if all((p == pos) or (board[p] == color) for p in mill):
                    return True
    return False

# Gets all opponent pieces that are legal to remove in the case of a mill
def get_mill_removals(state, opponent_color):
    board = state["board"]
    candidates = [pos for pos, occ in board.items() if occ == opponent_color and not forms_mill(board, pos, opponent_color)]
    if candidates:
        return candidates
    return [pos for pos, occ in board.items() if occ == opponent_color]

# Make a copy of the board to test moves on
def copy_state(state):
    return copy.deepcopy(state)

def change_turn(state):
    """Switch the turn in the state."""
    state["turn"] = "blue" if state["turn"] == "orange" else "orange"

def count_board_pieces(state, color):
    """Counts how many pieces of a given color are on the board."""
    return sum(1 for occ in state["board"].values() if occ == color)

# Generates every possible legal move from current state for player 'color'
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

# Returns the new state after applying a move, which is in tuple form (source, dest, removal)
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

    change_turn(new_state)
    return new_state

# Checks if game is over (no legal moves, a player has less than 3 pieces, or stalemate)
def is_terminal(state):
    for color in ["blue", "orange"]:
        if count_board_pieces(state, color) + state["hand"][color] < 3:
            return True
    if not generate_moves(state, state["turn"]):
        return True
    if state["mill_counter"] >= 20:
        return True
    return False

# Heuristic evaluation (STILL IN PROGRESS DECIDING VALUES)
def evaluate(state, player, is_root):
    opponent = "blue" if player == "orange" else "orange"
    
    if is_terminal(state):
        if count_board_pieces(state, player) + state["hand"][player] < 3 or not generate_moves(state, player):
            return -10000
        if count_board_pieces(state, opponent) + state["hand"][opponent] < 3 or not generate_moves(state, opponent):
            return 10000
        return 0

    my_pieces_left = count_board_pieces(state, player) + state["hand"][player]
    opp_pieces_left = count_board_pieces(state, opponent) + state["hand"][opponent]
    material = 100 * (my_pieces_left - opp_pieces_left)

    my_moves = len(generate_moves(state, player))
    opp_moves = len(generate_moves(state, opponent))
    mobility = 10 * (my_moves - opp_moves)

    strategic_positions = {"d2", "d6", "b4", "f4"}
    my_control = sum(1 for pos in strategic_positions if state["board"].get(pos) == player)
    opp_control = sum(1 for pos in strategic_positions if state["board"].get(pos) == opponent)
    control = 20 * (my_control - opp_control)

    return material + mobility + control

# Minimax with alpha beta pruning applied at a specific depth
def alphabeta(state, depth, alpha, beta, maximizing_player, player, start_time, is_root=False):
    if time.time() - start_time > TIME_LIMIT * 0.95:
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
    else:
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

# Runs minimax alpha-beta pruning at different depth lengths until time is up
def iterative_deepening(state, player):
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
    return best_move

# Converts a move string from the referee to a tuple (source, dest, removal)
def parse_move(move_str):
    parts = move_str.strip().split()
    if len(parts) != 3:
        raise ValueError("Invalid move format")
    return tuple(parts) 

# Converts a tuple into a move string and applies either h1 or h2 based on player color
def move_to_string(move, player_color):
    source, dest, removal = move
    if source == "h":
        source = "h1" if player_color == "blue" else "h2"
    return f"{source} {dest} {removal}"


def main():
    # Read initial color
    player_color = input().strip().lower()
    log_debug("My color is {}".format(player_color))
    
    state = initial_state()
    state["turn"] = "blue" 
    
    if player_color == "blue":
        move = iterative_deepening(state, player_color)
        if move is None:
            sys.exit("No valid move found")
        state = apply_move(state, move)

        log_debug("Our move: {} and color {}".format(move, player_color))
        print(move_to_string(move, player_color), flush=True)
        log_debug("Our move: {} and color {}".format(move_to_string(move, player_color), player_color))
    
    # Main loop
    while True:
        try:
            log_debug("TEST 1 {}".format(player_color))
            game_input = input().strip()
            log_debug("TEST FROM AARON {} game input: {}".format(player_color, game_input))
            if game_input.startswith("END"):
                break

            opp_move = parse_move(game_input)
            log_debug("TEST 3 {}".format(player_color))
            state = apply_move(state, opp_move)

            if is_terminal(state):
                break
            log_debug("TEST 4 {}".format(player_color))

            move = iterative_deepening(state, player_color)
            log_debug("TEST 5 {}".format(player_color))
            if move is None:
                break
            state = apply_move(state, move)
            log_debug("FINAL MOVE: {}".format(move_to_string(move, player_color)))
            print(move_to_string(move, player_color), flush=True)

            if is_terminal(state):
                break

        except EOFError:
            break

if __name__ == "__main__":
    main()