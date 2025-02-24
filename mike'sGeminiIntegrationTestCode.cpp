#include <iostream>
#include <vector>
#include <string>
#include <cmath>

using namespace std;

/**
 * @brief Create a string that explains how to play Lasker Morris to the Gemini AI
 * 
 * @return A string that explains the rules of Lasker Morris
 */
string makeLaskerMorrisRules() {
    //Base rules that are easier to just type our hardcoded
    string laskerMorrisRules = "The game is Lasker Morris. There are two players: blue and orange. Each player starts with 10 stones in their hand and 0 on the board. Players take turns placing stones on the board, or moving pieaces already on the board to an adjacent open space. When a player forms 3 stones in a row, it forms a mill, and that player can remove one of the opponent's stones that are on the board and not in a mill. The game is won when a player reduces their oponent to only have 2 stones, or a tie occurs if there are 20 moves without a mill formed. When a player has only 3 pieces remaining, they can move to any open space, no longer limited to adjacent spaces. The game board is configured as follows, giving the name of a legal space followed by the names of all spaces adjacent to it. ";
    
    for(string position : AJACENCY) { //Prints out each position and its adjacencies, so gemini will know how to board works

        laskerMorrisRules += position + " is adjacent to ";
        bool first = true;

        for(string neighbor : AJACENCY[position]) {
            if(!first) laskerMorrisRules += ", ";
            else laskerMorrisRules += neighbor; first = false;
        }

        laskerMorrisRules += ". ";
    }
}

/**
 * @brief Create a string that explains the current state of the game to the Gemini AI
 * 
 * @param state The current state of the game
 * @param player The player to explain the state to
 * 
 * @return A string that explains the current state of the game
 */
string makeGeminiPrompt(State state, string player) {
    string opponent = (player == "orange") ? "blue" : "orange"; //Assign opponent value
    string geminiBoard = "The current player is " + player + ". ";

    //Count the number of pieces in hand and on the board for each player
    int playerPieces = count_board_pieces(state, player);
    int opponentPieces = count_board_pieces(state, opponent);

    geminiBoard += "The player has " + to_string(state.hand[player]) + " pieces in hand and " + to_string(playerPieces) + " pieces on the board. ";
    geminiBoard += "The opponent has " + to_string(state.hand[opponent]) + "pieces in hand " + to_string(opponentPieces) + " pieces on the board. ";

    geminiBoard += "The board is as follows: ";
    bool first = true;
    for(string position : state.board) {
        if(!first) geminiBoard += ", ";
        else geminiBoard += position + " " + state.board[position]; first = false;
    }
    
}

string laskerMorrisRules = makeLaskerMorrisRules(); //Generates a string with the base rules of the game

client = genai.Client(api_key="AIzaSyCGqDVXUI2wja07H2J2SjcG8wPG4q1qu_s") // **AIAIAI** In python, Generates gemini client

/**
 * @brief Gives the Gemini AI the current state of the game to recieve the best next move from it
 * 
 * @param state The current state of the game
 * @param player The player to get the move for
 * 
 * @return The move the Gemini AI wants to make
 */
string getGeminiMove(State state, string player) {

    string geminiPrompt = makeGeminiPrompt(state, player);

    // **AIAIAI** In python, Gives prompt to the Gemini AI to generate the best move based on the current state of the game and the rules we gave it.
    response = client.models.generate_content( model="gemini-2.0-flash", config=types.GenerateContentConfig(system_instruction=laskerMorrisRules), contents=[geminiPrompt])

    return response.text; //The string representation of Gemini's response
}