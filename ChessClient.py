import paramiko
from stockfish import Stockfish

#SSH client and stockfish engine objects
ssh_client = paramiko.SSHClient()
sfengine = Stockfish("C:\\Users\\svein\\Desktop\\stockfish_15_win_x64_popcnt\\stockfish_15_x64_popcnt.exe")

#List to store all the moves being done
moves = []

###TESTING ONLY###
#moves = ["e2e4", "e7e6", "g1f3", "g8f6", "e4e5", "f6d5", "c2c4", "d5b6", "d2d4", "d7d6", "b1c3", "b8c6", "e5d6", "d8d6", "c4c5", "d6d7", "c5b6", "a7b6", "f1d3", "c6d4", "f3d4", "d7d4", "d3b5", "d4d7", "b5d7", "c8d7", "c1f4", "c7c5", "d1d3", "h7h6", "c3b5", "g7g5", "b5c7", "e8e7", "e1c1", "a8d8", "f4d6", "e7f6", "d6e5", "f6e5", "d3f3", "d7c6", "h1e1", "c6e4"]
#sfengine.set_position(moves)
###TESTING ONLY###

#Creates an SSH terminal to communicate with ev3 brick.
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect('Team14Brick', username='robot', password='maker')

#Runs main.py on ev3 brick.
stdin, stdout, stderr = ssh_client.exec_command('brickrun -r -- pybricks-micropython ~/Chess/main.py')
sfengine.set_skill_level(0)

#Checks if the move given is a special type (capture, castle, etc.)
def check_move(move):
    movesf = move
    #Checks what type of capture the move is (if any), and modifies string to reflect this
    if sfengine.will_move_be_a_capture(move) == Stockfish.Capture.DIRECT_CAPTURE:
        move = move + "dc"
    elif sfengine.will_move_be_a_capture(move) == Stockfish.Capture.EN_PASSANT:
        move = move + "pc"

    #Checks if move is castle on white side
    if movesf == "e1c1" or movesf == "e1g1":
        fromSquare = movesf[0:2]
        toSquare = movesf[2:]
        if sfengine.get_what_is_on_square(fromSquare) == Stockfish.Piece.WHITE_KING:
            #Checks if it's a queen- or king-side castle
            if toSquare == "c1":
                move = move + "rq"
            elif toSquare == "g1":
                move = move + "rk"
    #Same check on black side
    if movesf == "e8c8" or movesf == "e8g8":
        fromSquare = movesf[0:2]
        toSquare = movesf[2:]
        if sfengine.get_what_is_on_square(fromSquare) == Stockfish.Piece.BLACK_KING:
            if toSquare == "c8":
                move = move + "rq"
            elif toSquare == "g8":
                move = move + "rk"
    #If no modifications have been done, nn is added to the ends of the string to prevent indexing exceptions.
    if len(move) < 5:
        move = move + "nn"
    return move

while True:
    global selection
    print("Type \"white\" or \"black\" to choose a side:")
    selection = input()
    if selection.lower() == "white" or selection.lower() == "black":
        break
    else:
        print("Please type a valid selection")


running = True
while running:
    if selection == "black":
        #Move is fetched from stockfish
        sfMove = sfengine.get_best_move()
        #Move is sent to ev3
        nextMove = check_move(sfMove)
        stdin.write(nextMove + '\n')
        stdin.flush()

        #New position is set
        moves.append(sfMove)
        sfengine.set_position(moves)
        selection = ""
    #Checks for checkmate
    if sfengine.get_best_move() == None:
        print("Checkmate. Stockfish has won.")
        break
    #Reads from ev3 terminal
    print(stderr.readline().strip("\n"))

    #Sends input to ev3. Checks with stockfish if the input is a valid move.
    while True:
        try :
            #Takes user input. Makes a copy of the string to add extra information. The original move is fed directly into stockfish.
            movesf = input()
            movetemp = movesf
            #If a pawn is moved to the other side, it is automatically promoted to queen. This is to save ourselves from adding a lot of code for very niche cases where a queen is not optimal.
            if movesf[3] == "8" and sfengine.get_what_is_on_square(movesf[0:2]) == Stockfish.Piece.WHITE_PAWN:
                movesf = movesf + "q"
            if movesf[3] == "1" and sfengine.get_what_is_on_square(movesf[0:2]) == Stockfish.Piece.BLACK_PAWN:
                movesf = movesf + "q"
            if movesf.lower() == "resign":
                #User resigns
                running = False
                break
            #Checks if the move is legal. Repeats loop is it isn't
            if sfengine.is_move_correct(movesf):
                #Calls function to modify string
                move = check_move(movetemp)

                stdin.write(move + '\n')
                stdin.flush()
                stderr.readline()
                break
            else:
                print("Please input a valid move")
        except Exception as e:
            print("Input is invalid, please try again.")
    if not running:
        print("Pathetic")
        break

    #Reads from ev3 terminal
    print(stderr.readline().strip("\n"))

    #Move is put into stockfish, and position is set
    moves.append(movesf)
    sfengine.set_position(moves)

    #Checks for checkmate
    if sfengine.get_best_move() == None:
        print("Checkmate. You won!")
        break
    sfMove = sfengine.get_best_move()
    
    #Move is sent to ev3
    nextMove = check_move(sfMove)
    stdin.write(nextMove + '\n')
    stdin.flush()
    stderr.readline()

    moves.append(sfMove)
    sfengine.set_position(moves)

    #Reads from ev3 terminal
    print(stderr.readline().strip("\n"))
    
    
    

