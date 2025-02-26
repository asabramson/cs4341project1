import sys
import time
import random
import re
import copy
from google import genai
from google.genai.errors import ClientError

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


# USED FOR DEBUGGING TO SEPARATE TEXT FILE TO NOT CONFUSE REFEREE WITH STDOUT
def log_debug(message):
    with open("debuggg.txt", "a") as f:
        f.write(message + "\n")

#* @brief Read Gemini API key from a git hidden text file
#* 
#* @return The API key
def read_api_key():
    f = open("hush_secret.txt", "r")
    api_key = f.readline().strip()
    f.close()
    return api_key


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


# ---------------------------------------------------------------

# -------------    GEMINI RELATED FUNCTIONS    ------------------

def make_lasker_morris_rules(color):
    opponent_color = "blue" if color == "orange" else "orange"
    laskerMorrisRules = "Hello! I was hoping you would be able to help me decide the best move option based on a given board state for the game Lasker Morris. The game is very similar to Nine Men's Morris, with the only real difference being that players can make adjacent moves with stones already on the board before exhausting all stones from their hand, where in Nine Men's Morris you must play all stones from your hand to be able to make adjacent moves from already placed stones. For our game, there are two players: blue and orange. The blue player will always make the first move. Each player starts with 10 stones in their hand and 0 on the board. Players take turns placing stones on the board, or moving pieaces already on the board to an adjacent open space. When a player forms 3 stones in a row, it forms a mill, and that player can remove one of the opponent's stones that are on the board and not in a mill. The game is won when a player reduces their oponent to only have 2 stones, or a tie occurs if there are 20 moves without a mill formed (game stalemate). When a player has only 3 pieces remaining, they can move to any open space, no longer limited to adjacent spaces. The game board is labeled with numbers 1 through 7 for each row (bottom row is row 1, top is row 7), and letters a through g for each column (leftmost column is column a, rightmost is column g). For example, the bottom left board space is 'a1' and the top right board space is 'g7'. The game board is configured as follows, giving the name of a legal space followed by the names of all spaces adjacent to it: "

    for position, neighbors in ADJACENCY.items():
        adjacent_to = position + " is adjacent to "
        for neighbor in neighbors:
            adjacent_to += neighbor + ", "
    
        laskerMorrisRules += adjacent_to[:-1] # remove last comma
        laskerMorrisRules += ". "

    laskerMorrisRules += "After you decide the best move, you can present the move in the following format: (source, destination, removal). Source is the space that the piece is being moved from. If being placed from the hand, you can use 'h' instead of a space's coordinates. If we are the blue player, 'h1' should be used, and if we are the orange player, 'h2' should be used. Destination is the space that our piece is being moved to. Removal is the coordinates of the opponent piece that should be removed in the event that we form a mill. On turns where we do not form a mill, this should be left as 'r0' to signify no removal. Some examples of moves include: (h1 a1 r0), given we are the blue player, move a piece from our hand to space a1, do not remove an opponent piece, (h2 a1 r0), given we are the orange player, move a piece from our hand to space a1, do not remove an opponent piece, (a1 a4 r0), move a piece from a1 to a4, do not remove an opponent piece, (a4 a7 b2), given we form a mill from this move, move a piece from a4 to a7 and remove an opponent piece from b2. When outputting the best move, try to only output the move with as little else as possible so that the move can be processed as quickly as possible. Make sure to have the move as the first time that you print, as the referee needs to see it before any explanation. Please be aware that d4 is not a valid space, please do not place it there. "
    laskerMorrisRules += "For this game, our player color is {} and the opponent is {}.".format(color, opponent_color)

    return laskerMorrisRules

def make_gemini_prompt(state, color, opp_move):
    opponent_color = "blue" if color == "orange" else "orange"
    player_pieces = count_board_pieces(state, color)
    opponent_pieces = count_board_pieces(state, opponent_color)
    player_hand = state["hand"][color]
    opponent_hand = state["hand"][opponent_color]

    board_info = "Our player has {} pieces in hand and {} pieces on the board. The opponent has {} pieces in hand and {} pieces on the board. The following information describes each space and the color of the piece currently there, if neither player is occupying the space, None will be displayed. ".format(player_hand, player_pieces, opponent_hand, opponent_pieces)

    board = state["board"]
    for pos, occ in board.items():
        board_info += "Space: {} Current piece there: {} ".format(pos, occ)
    board_info += "The opponent's last move was {}".format(opp_move)

    return board_info


#* @brief Extracts the move from Gemini AI's response
#*
#* @param response The full response string from Gemini AI
#*
#* @return List containing the move components (source, destination, removal), or None if not found
def extract_move_from_gemini(response):
    match = re.search(r'\(([^)]+)\)', response)
    if match:
        return tuple(match.group(1).split())
    return None


#* @brief Validates if a move is legal based on the current game state
#*
#* @param state The current game state
#* @param move The move tuple (source, destination, removal)
#*
#* @return Boolean indicating whether the move is valid
def validate_move(state, move):
    possible_moves = generate_moves(state, state["turn"])
    return move in possible_moves


#* @brief Handles move correction if an invalid move is detected
#*
#* @return None, indicating the need for a new move request
def request_corrected_move():
    reprompt = "The last move you generated was marked as invalid, which may be due to one of the following reasons: the piece was played from hand when we have no pieces left in hand, a piece on the board attempted to move to a non-adjacent space, the piece ended up on a space with a piece already there, an invalid coordinate was given, or another similar reason. Would you mind regenerating the move based on the last given board state?"
    return reprompt

#* @brief Generates a fallback move in case the LLM fails to provide a valid one
#*
#* @param state The current game state
#*
#* @return A randomly selected valid move from possible moves
def generate_fallback_random_move(state):
    possible_moves = generate_moves(state, state["turn"])
    if possible_moves:
        return random.choice(possible_moves)
    return None

#* @brief Processes Gemini AI's move by extracting it OR generating a fallback move
#*
#* @param state The current game state
#* @param gemini_response The response from Gemini AI containing the suggested move
#*
#* @return the valid AI generated move OR a fallback move
def process_gemini_response(state, gemini_response):
    move = tuple(extract_move_from_gemini(gemini_response))
    if not move or not validate_move(state, tuple(move)):
        fallback_move = generate_fallback_random_move(state)
        log_debug("**********LLM move invalid. Using fallback move: {}".format(fallback_move)) 
        log_debug(f"Invalid move detected: {move}") 

        return fallback_move
    return move

def main():
    # Read initial color
    log_debug("OUR COLOR IS:")
    player_color = input().strip().lower()
    log_debug("OUR COLOR IS: {}".format(player_color))

    lasker_morris_instructions = make_lasker_morris_rules(player_color)

    secret_key = read_api_key()

    client = genai.Client(api_key=secret_key)
    chat = client.chats.create(model='gemini-2.0-flash')
    try:
        response = chat.send_message(lasker_morris_instructions)
    except ClientError as e:
        error_message = e.args[0]
        if "429" in error_message:
            error_code = 429
            time.sleep(5)
            response = chat.send_message(lasker_morris_instructions)

    log_debug("FIRST GEMINI CONTACT: {} \n ----------------------------------- \n".format(response.text))
    
    state = initial_state()
    state["turn"] = "blue" 
    
    # Blue makes the first move
    if player_color == "blue":
        board_update = make_gemini_prompt(state, player_color, "none, this is the first move of the game")
        try:
            response = chat.send_message(board_update)
        except ClientError as e:
            error_message = e.args[0]
            if "429" in error_message:
                error_code = 429
                time.sleep(5)
                response = chat.send_message(board_update)
        log_debug("Raw move: {}\n".format(response.text))
        move = process_gemini_response(state, response.text)
        log_debug("Processed move: {}\n".format(move))
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

            board_update = make_gemini_prompt(state, player_color, opp_move)
            try:
                response = chat.send_message(board_update)
            except ClientError as e:
                error_message = e.args[0]
                if "429" in error_message:
                    error_code = 429
                    time.sleep(5)
                    response = chat.send_message(board_update)
            log_debug("Raw move: {}\n".format(response.text))
            move = process_gemini_response(state, response.text)
            log_debug("Processed move: {}\n".format(move))
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