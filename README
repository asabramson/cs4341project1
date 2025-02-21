Project by Aaron Abramson, Michael Conroy, and Peter Czepiel

a. Project Member Responsibilities
    Aaron: Provided majority of initial code base and function structure of lasker morris rules, handled most of the technical issues. Debugged issues relating to referee communication
    Michael: Offered general debugging assistance, expanded and researched heuristic function ideas and strategies for this and future for Part 3, also provided documentation.
    Peter: Offered general debugging assistance, cleaned up and consolidated code structure, thoroughly commented throughout, expanded on Michael's heusristic strategies
____________________________________________________________________________________________________________________
b. Running Instructions
    1. Next run the referee program (https://github.com/jake-molnia/CS4341-referee) with the JD AI Player by running the command "cs4341-referee laskermorris -p1 "python jd.py" -p2 "python jd.py" --visual" in your terminal
        - Other players can be used by swapping out 'jd.py' with the filename of another player
        - Alternate game configurations can be setup using the different commands detailed in the ref's README
____________________________________________________________________________________________________________________
c. Utility Function
    The utility function for the JD AI, contained within the 'evaluate' function. A helper function 'is_terminal' checks if the game is in an ending state (win, loss, draw), and if so, it checks the total of the number of pieces on the board and in the hands of both players in a given board configuration, and if the player has less than 3, the utility value is set to -10000 (we lose, bad outcome). If the opponent has less than 3 pieaces, the value is 10000 (we win, good outcome).
____________________________________________________________________________________________________________________
d. Evaluation Function
    The evaluation function for the JD AI is the 'evaluate' function. It first checks if the current board configuration is terminal, and if so applies the utility function. If not, the board goes through a series of heuristic checks based on the current board state (described below). 
____________________________________________________________________________________________________________________
e. Heuristic Checks
    Point allocations for the evaluation function are as follows: 100 points per number of our pieces (-100 for each opponent piece), 10 points per number of moves available from that space (-10 for number of moves available from each opponent piece), and 20 points per number of pieces in 'strategic positions' (d2, d6, b4, f4, these spaces have the most edges with other spaces) (-20 per opponent piece in strategic position). Most importantly, a move scoring a mill is worth 5000, and a move blocking an opponent's mill is worth 3000. The score is added up and returned as a total.
____________________________________________________________________________________________________________________
f. Results
    a. Tests
        We tested our AI player against itself and against a random move player. Against itself, it had a number of different outcomes due to a level of uncertainty in our implementation (some win/loss games, some draws). Our random player contained a bug with referee communication, so results from those games were not 100% useful, but those that did go through were always wins
    b. Strengths and Weaknesses
        Some of the stronger aspects of the JD program are: In the beginning it plays quite offensively and defensively strong
        Some of the weaker aspects of the JD AI are: As the game progresses, the uncertainty of the AI player's choices increases in an effort to confuse the opponent, however, this sometimes can backfire by not choosing an obvious good move (we want to work on improving this idea for Part III)
        Our group already has plans for ways to improve JD for further use, with continued development into different additions to the heuristic functions to reflect more thorough and advanced strategies!
