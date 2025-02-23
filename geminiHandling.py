import re
import random

#* @brief Extracts the move from Gemini AI's response
#*
#* @param response The full response string from Gemini AI
#*
#* @return List containing the move components (source, destination, removal), or None if not found
def extract_move_from_gemini(response):
    match = re.search(r'\((.*?)\)', response)
    if match:
        return match.group(1).split()
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
def request_corrected_move(state):
    print("Invalid move suggested. Requesting a new move from Gemini...", flush=True)
    # Logic to re-prompt Gemini AI for a valid move (not implemented here, will come from Michael's code)
    return None


#* @brief Generates a fallback move in case the LLM fails to provide a valid one
#*
#* @param state The current game state
#*
#* @return A randomly selected valid move from possible moves
def generate_fallback_move(state):
    possible_moves = generate_moves(state, state["turn"])
    if possible_moves:
        return random.choice(possible_moves)
    return None


#* @brief Processes Gemini AI's move by extracting, validating, and executing it
#*
#* @param state The current game state
#* @param gemini_response The response from Gemini AI containing the suggested move
#*
#* @return The updated game state after applying a valid move, or requests a new move if invalid
def process_gemini_move(state, gemini_response):
    move = extract_move_from_gemini(gemini_response)
    if not move or not validate_move(state, tuple(move)):
        fallback_move = generate_fallback_move(state)
        if fallback_move:
            print("LLM move invalid. Using fallback move:", move_to_string(fallback_move, state["turn"]), flush=True)
            state = apply_move(state, fallback_move)
            return state
        return request_corrected_move(state)
    
    move_tuple = tuple(move)
    state = apply_move(state, move_tuple)
    print(move_to_string(move_tuple, state["turn"]), flush=True)
    return state


# Example usage:
# gemini_response = "Move from h1 to d1. This will not form a mill, so no removal is necessary, so (h1 d1 r0)."
# state = initial_state()
# updated_state = process_gemini_move(state, gemini_response)
